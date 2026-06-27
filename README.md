# 🏠 宜居助手 — AI 驱动的二手房交易平台

一个基于 **Django + Vue 3 + LangGraph** 的全栈 Web 应用，集成 AI 智能助手，支持房源搜索、个性化推荐、政策问答和流式对话。

> 🎓 作者：大三在读 | 技术栈：Python / Django / Vue 3 / LangGraph / RAG

---

## ✨ 功能模块

| 模块 | 功能 | 技术实现 |
|------|------|----------|
| 🏡 **房源展示** | 多条件筛选、分页、排序 | Django DRF + MySQL |
| 👤 **用户系统** | 注册/登录、JWT 认证、个人信息 | DRF + SimpleJWT |
| ❤️ **收藏系统** | 收藏/取消收藏房源 | RESTful API |
| 🧠 **智能推荐** | 基于用户收藏偏好的房源推荐 | 自研推荐引擎（内容协同过滤） |
| 🤖 **AI 助手** | 自然语言搜房、政策问答、选房建议 | LangGraph Agent + DeepSeek |
| 📚 **RAG 知识库** | 购房资格、贷款政策、税费、交易流程 | ChromaDB + BGE 向量检索 |
| ⚡ **流式对话** | AI 回复逐字输出 | SSE + Fetch ReadableStream |
| 🕷️ **数据采集** | 房天下/安居客爬虫 | BeautifulSoup + Selenium 反检测 |

---

## 🧱 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    Vue 3 前端                        │
│  Vite + Pinia + Vue Router + Axios                  │
│  ├─ 房源搜索/筛选/分页                               │
│  ├─ 用户登录/收藏                                    │
│  └─ AI 助手（SSE 流式对话）                          │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/SSE
┌──────────────────▼──────────────────────────────────┐
│                 Django REST API                      │
│  ┌──────────┬──────────┬────────────────────┐      │
│  │  Users   │ Listings │    Assistant        │      │
│  │  认证    │  房源CRUD │  ┌──────────────┐   │      │
│  │  JWT     │  推荐引擎 │  │ LangGraph    │   │      │
│  └──────────┴──────────┤  │ Agent        │   │      │
│                        │  │ ├ search_db  │   │      │
│                        │  │ └ search_kb  │   │      │
│                        │  └──────┬───────┘   │      │
│                        │         │            │      │
└────────────────────────┼─────────┼────────────┘      │
                         │         │                   │
            ┌────────────▼───┐ ┌──▼──────────────┐    │
            │    MySQL       │ │   ChromaDB      │    │
            │  房源/用户数据  │ │  RAG 向量知识库  │    │
            └────────────────┘ └─────────────────┘    │
```

---

## 🤖 AI 助手工作流

```
用户提问 ──→ LangGraph Agent ──→ DeepSeek LLM 判断意图
                                    │
                    ┌───────────────┼───────────────┐
                    ▼                               ▼
            search_houses()                 search_knowledge()
            查 MySQL 房源                   查 ChromaDB 向量库
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                            LLM 综合生成回复
                                    │
                                    ▼
                          SSE 流式输出到前端
```

### Agent 能力

- **Tool Calling** — LLM 自动判断需要查数据库还是查知识库
- **多轮对话** — MemorySaver 保持上下文，追问无需重复描述需求
- **RAG 检索** — 5 篇房产知识文档向量化，覆盖购房资格/贷款/税费/交易流程/选房技巧
- **异常自愈** — 工具调用失败自动降级，悬空状态自动清理

---

## 🚀 快速启动

### 环境要求

- Python 3.12+
- Node.js 22+
- MySQL 8.0+

### 1. 后端

```bash
cd django_project

# 安装依赖
pip install -r ../requirements.txt

# 配置数据库（编辑 django_project/settings.py 中的 DATABASES）
# 配置 API Key（编辑 .env）
#   DEEPSEEK_API_KEY='你的Key'
#   DEEPSEEK_API_BASE='https://api.deepseek.com'

# 数据库迁移
python manage.py migrate

# 导入房源数据（如果有 CSV）
python manage.py import_house

# 构建 RAG 向量库（首次需下载 embedding 模型）
python manage.py ingest_docs

# 启动后端
python manage.py runserver
```

### 2. 前端

```bash
cd my_vue_app

npm install
npm run dev
```

访问 `http://localhost:5173` → 注册/登录 → 点击「🤖 AI 助手」开始对话。

---

## 📂 项目结构

```
myself_project/
├── django_project/              # Django 后端
│   ├── assistant/               # AI 助手模块
│   │   ├── agent.py             #   LangGraph Agent 编排
│   │   ├── retriever.py         #   RAG 检索引擎
│   │   ├── views.py             #   Chat API（普通 + SSE 流式）
│   │   ├── urls.py              #   路由
│   │   └── management/commands/
│   │       └── ingest_docs.py   #   向量库构建命令
│   ├── listings/                # 房源模块
│   │   ├── models.py            #   数据模型（HouseListing, Favorite）
│   │   ├── views.py             #   搜索/收藏/推荐 API
│   │   ├── recommendation.py    #   推荐引擎
│   │   └── serializers.py       #   序列化
│   ├── users/                   # 用户模块
│   │   ├── models.py            #   自定义用户模型
│   │   └── views.py             #   注册/登录 API
│   └── django_project/          # Django 配置
│       ├── settings.py          #   数据库/JWT/CORS/DeepSeek
│       └── urls.py              #   主路由
├── my_vue_app/                  # Vue 3 前端
│   └── src/
│       ├── views/
│       │   ├── Assistant.vue    #   AI 助手对话页（流式渲染）
│       │   ├── Home.vue         #   房源首页
│       │   ├── Favorites.vue    #   收藏页
│       │   └── Login.vue        #   登录/注册
│       ├── components/
│       │   ├── AppHeader.vue    #   导航栏
│       │   └── FilterSidebar.vue#   筛选侧边栏
│       ├── api/                 #   API 封装
│       └── router/              #   路由配置
├── rag_docs/                    # RAG 知识文档（不入库）
│   ├── policies/                #   政策类
│   │   ├── 购房资格.txt
│   │   └── 贷款政策.txt
│   └── guides/                  #   指南类
│       ├── 交易流程.txt
│       ├── 税费指南.txt
│       └── 选房技巧.txt
├── spider.py                    # 房天下爬虫
├── spider2.py                   # 安居客爬虫（Selenium 反检测）
└── requirements.txt             # Python 依赖
```

---

## 📸 界面预览

| 首页 | AI 助手 |
|------|---------|
| 房源列表 + 筛选 + 推荐 | 流式对话 + 快捷提问 |

> 启动项目后访问 `http://localhost:5173` 即可体验。

---

## 📝 待完善

- [ ] 单元测试覆盖
- [ ] Docker 容器化部署
- [ ] Elasticsearch 全文搜索替代 MySQL LIKE
- [ ] 推荐引擎引入协同过滤
- [ ] 对话历史持久化到数据库
- [ ] CI/CD 流水线

---

## 📄 License

MIT
