"""
RAG 检索引擎
在 LangGraph Agent 中被调用，根据用户问题检索相关知识文档

用法：
  from assistant.retriever import retrieve
  docs = retrieve("广州首套房首付比例是多少")
  # → [{"content": "...", "source": "贷款政策.txt", "score": 0.92}, ...]
"""
from pathlib import Path
from langchain_community.vectorstores import Chroma


CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"

_vectorstore = None
_embedding_model = None


def _get_embedding_model():
    """延迟加载 embedding 模型，避免 import 时就下载"""
    global _embedding_model
    if _embedding_model is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        _embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        if not CHROMA_PERSIST_DIR.exists():
            raise FileNotFoundError(
                f"向量库不存在: {CHROMA_PERSIST_DIR}\n"
                "请先运行: python manage.py ingest_docs"
            )
        _vectorstore = Chroma(
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=_get_embedding_model(),
            collection_name="real_estate_kb",
        )
    return _vectorstore


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    根据用户问题检索最相关的知识文档片段

    Args:
        query: 用户问题，如 "北京购房需要什么条件"
        top_k: 返回最相关的 k 个文本块

    Returns:
        [{"content": "文本内容", "source": "文件名", "category": "分类", "score": 相似度}, ...]
    """
    try:
        vs = get_vectorstore()
    except (FileNotFoundError, ImportError) as e:
        return [{"content": str(e), "source": "系统", "category": "error", "score": 0}]

    try:
        docs_with_scores = vs.similarity_search_with_relevance_scores(query, k=top_k)
    except Exception:
        return []

    results = []
    for doc, score in docs_with_scores:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "未知"),
            "category": doc.metadata.get("category", "未知"),
            "score": round(score, 4),
        })
    return results


def format_for_llm(retrieved_docs: list[dict]) -> str:
    """
    将检索结果格式化为 LLM 可理解的文本
    """
    if not retrieved_docs:
        return "未找到相关知识文档。"

    parts = ["以下是与用户问题相关的房产知识，请基于这些信息回答：\n"]
    for i, doc in enumerate(retrieved_docs, 1):
        parts.append(
            f"【参考资料 {i}】来源: {doc['source']} ({doc['category']})\n"
            f"{doc['content']}\n"
        )
    return "\n".join(parts)
