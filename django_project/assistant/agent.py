"""
LangGraph Agent — 房产 AI 助手核心
将数据库查询、RAG 知识检索、LLM 对话编排为一个智能体

工具：
  1. search_houses — 查房源数据库（结构化查询）
  2. search_knowledge — 查知识文档（RAG 向量检索）

流程：
  用户输入 → LLM 判断需要哪些工具 → 执行工具 → LLM 生成回复 → 返回
                           ↑                              |
                           └── 需要更多信息，循环 ←─────────┘
"""
from typing import Literal

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessageChunk

from django.conf import settings
from listings.models import HouseListing
from .retriever import retrieve, format_for_llm

# ── LLM 配置（延迟初始化）──────────────────────────────
_llm = None
_tools_bound_llm = None
_agent = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
            temperature=0.3,
            max_tokens=2000,
            streaming=True,
        )
    return _llm


def _get_llm_with_tools():
    global _tools_bound_llm
    if _tools_bound_llm is None:
        _tools_bound_llm = _get_llm().bind_tools(TOOLS)
    return _tools_bound_llm

# ── System Prompt ─────────────────────────────────────
SYSTEM_PROMPT = """你是"宜居助手"，一个专业的房产咨询 AI。你可以帮助用户：

1. 搜索房源：根据用户的需求（城市、预算、户型、面积等）查询数据库中的房源
2. 解答政策：回答购房资格、贷款政策、税费、交易流程等知识类问题
3. 选房建议：根据用户需求提供户型、楼层、朝向等选房建议

核心原则：
- 回答要具体、准确，引用真实数据和政策条款
- 如果用户想找房源，先确认城市、预算范围、户型偏好再搜索
- 如果搜索结果为空，主动建议放宽条件或推荐相近区域
- 回答政策类问题时，结合 search_knowledge 返回的内容，不要编造
- 金额默认为人民币"万元"，面积默认为"平方米"
- 语气友好、专业，像一位有经验的房产经纪人"""


# ── 工具定义 ──────────────────────────────────────────

@tool
def search_houses(
    city: str,
    max_total_price: float = None,
    min_total_price: float = None,
    house_type: str = None,
    min_size: float = None,
    max_size: float = None,
    limit: int = 5,
) -> str:
    """
    搜索房源数据库。当用户想找房子、比较房源、了解某城市有什么房子时调用。

    Args:
        city: 城市名称，如"北京""广州""上海"
        max_total_price: 最高总价（万元），如用户说"300万以内"则传300
        min_total_price: 最低总价（万元）
        house_type: 户型，如"三室一厅""两室一厅"
        min_size: 最小面积（平方米）
        max_size: 最大面积（平方米）
        limit: 返回结果数量上限，默认5
    """
    filter_params = {"city__icontains": city}
    if max_total_price:
        filter_params["total_price__lte"] = max_total_price
    if min_total_price:
        filter_params["total_price__gte"] = min_total_price
    if house_type:
        filter_params["house_type__icontains"] = house_type
    if min_size:
        filter_params["house_size__gte"] = min_size
    if max_size:
        filter_params["house_size__lte"] = max_size

    try:
        houses = HouseListing.objects.filter(**filter_params).order_by(
            "-created_time"
        )[:limit]
    except Exception as e:
        return f"查询房源时出错: {e}。请检查数据库是否已导入数据。"

    if not houses:
        return f"在{city}未找到匹配的房源。建议调整筛选条件或扩大搜索范围。"

    results = []
    for i, h in enumerate(houses, 1):
        results.append(
            f"{i}. {h.house_name}\n"
            f"   地址: {h.house_address}\n"
            f"   户型: {h.house_type} | 面积: {h.house_size}㎡ | {h.house_position} | {h.house_height}\n"
            f"   总价: {h.total_price}万 | 单价: {h.unit_price}元/㎡\n"
            f"   描述: {h.house_description}"
        )
    return "\n\n".join(results)


@tool
def search_knowledge(query: str) -> str:
    """
    搜索房产知识库。当用户询问购房资格、贷款政策、税费、交易流程、选房技巧等
    知识类问题时调用。不要用来搜索具体房源。

    Args:
        query: 用户想问的问题或关键词
    """
    try:
        docs = retrieve(query, top_k=4)
    except Exception as e:
        return f"知识库检索出错: {e}。请先运行 python manage.py ingest_docs 构建向量库。"
    if not docs:
        return "未找到相关知识。建议咨询当地住建部门或拨打12345热线了解最新政策。"
    return format_for_llm(docs)


TOOLS = [search_houses, search_knowledge]

# ── 图节点 ────────────────────────────────────────────

def llm_node(state: MessagesState) -> dict:
    """LLM 调用节点：决定调用工具还是直接回复"""
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # 确保消息列表中不存在悬空的 tool_calls（上一次异常可能残留）
    messages = _sanitize_messages(messages)

    response = _get_llm_with_tools().invoke(messages)
    return {"messages": [response]}


def _sanitize_messages(messages: list) -> list:
    """
    移除最后一条消息如果是悬空 tool_calls（没有紧随的 tool 结果），
    防止 DeepSeek 报 400：insufficient tool messages following tool_calls message
    """
    if not messages:
        return messages
    last = messages[-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        # 最后一条是 tool_calls 但没有对应的 tool 结果 → 移除
        return messages[:-1]
    return messages


def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    """判断 LLM 响应是否需要调用工具"""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "__end__"


# ── 构建图（延迟初始化）────────────────────────────────

def _get_agent():
    global _agent
    if _agent is None:
        builder = StateGraph(MessagesState)
        builder.add_node("llm", llm_node)
        builder.add_node("tools", ToolNode(TOOLS))
        builder.add_edge(START, "llm")
        builder.add_conditional_edges("llm", should_continue)
        builder.add_edge("tools", "llm")
        memory = MemorySaver()
        _agent = builder.compile(checkpointer=memory)
    return _agent


# ── 对外接口 ──────────────────────────────────────────

def chat(user_input: str, thread_id: str = "default") -> str:
    """
    和 AI 助手对话

    Args:
        user_input: 用户消息
        thread_id: 会话 ID，不同用户/会话使用不同 ID 以隔离上下文

    Returns:
        AI 助手的回复文本
    """
    config = {"configurable": {"thread_id": thread_id}}
    agent = _get_agent()
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        return result["messages"][-1].content
    except Exception as e:
        # 如果 state 损坏导致 LLM 调用失败，清空该会话重试一次
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Agent 调用失败，清理会话后重试: {e}")
        agent = _get_agent()
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id + "_retry"}},
        )
        return result["messages"][-1].content


def chat_stream(user_input: str, thread_id: str = "default"):
    """
    和 AI 助手对话（流式输出），逐 token yield

    用法:
      for token in chat_stream("北京首付多少"):
          print(token, end="", flush=True)
    """
    config = {"configurable": {"thread_id": thread_id}}
    agent = _get_agent()

    try:
        for chunk, _metadata in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                if not chunk.tool_calls and not chunk.additional_kwargs.get("tool_calls"):
                    yield chunk.content
    except Exception:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("流式调用失败")
        yield "抱歉，AI 助手暂时无法响应。"
