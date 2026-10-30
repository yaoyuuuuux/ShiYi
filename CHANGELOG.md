# 更新日志

## W1 · CLI 便贴 RAG（2026-10-30）

### 完成的功能

1. **便贴存取**：读便贴、记便贴、列便贴、按分类筛选（`backend/app/notes/`）。
2. **模型调用**：Qwen 聊天模型与 embedding 模型的 HTTP 客户端，超时 / 状态码 / 响应结构三道防线（`backend/app/clients/`）。
3. **向量化**：问题与便贴统一用 BGE-M3 编码成 1024 维向量（`clients/embedding.py`）。
4. **检索**：关键词简单基线 + embedding 语义检索；余弦相似度、维度校验、排序、top-k（`backend/app/retrieval/`）。
5. **RAG 回答**：把 top-k 原文和问题拼成 Prompt，交给 Qwen 生成一句话回答；先展示原文，再给出回答（`backend/app/rag/`）。
6. **CLI**：`notes list` / `notes add` / `ask`（`backend/app/cli/main.py` + `scripts/rag_cli.py`）。
7. **测试**：18 个纯函数 / HTTP mock 测试，不调真实 API（`backend/tests/`）。

### 目录结构

```text
ShiYi/
├── backend/
│   ├── app/
│   │   ├── config.py              # 路径 / Key / 模型名 / top_k
│   │   ├── main.py                # FastAPI 入口（W2）
│   │   ├── api/                   # W2 路由
│   │   ├── cli/main.py            # CLI：notes list/add + ask
│   │   ├── clients/
│   │   │   ├── http.py            # 通用 POST JSON + 错误翻译
│   │   │   ├── qwen.py            # QwenClient：聊天模型请求/响应
│   │   │   └── embedding.py       # EmbeddingClient：文本 → 向量
│   │   ├── retrieval/
│   │   │   ├── keyword.py         # 关键词打分/排序（W1 简单基线）
│   │   │   └── semantic.py        # embedding + 余弦 + top-k
│   │   ├── notes/
│   │   │   ├── repository.py      # JSON 读写（原子写入）
│   │   │   └── service.py         # 增/查/分类筛选/拼 embedding 文本
│   │   ├── rag/
│   │   │   ├── pipeline.py        # 检索 → Prompt → 回答
│   │   │   └── prompt.py          # 拼 Prompt
│   │   ├── schemas/note.py        # Note / ScoredNote
│   │   ├── agents/                # LangGraph（W5）
│   │   ├── models/                # SQLAlchemy（W2）
│   │   └── utils/                 # text.py 文本预处理 / log.py 日志
│   ├── data/notes.json            # 本机便贴数据（不入库）
│   ├── tests/                     # 18 个测试
│   └── requirements.txt           # requests / python-dotenv
├── scripts/
│   ├── rag_cli.py                 # CLI 薄入口
│   └── embedding_demo.py          # 关键词 vs embedding 对比
├── docs/                          # 产品 / 学习文档
├── CHANGELOG.md                   # 本文件
├── CLAUDE.md
└── README.md
```

### 说明

- `scripts/` 只放入口和演示，不写业务逻辑；每个功能在 `backend/app/` 只有一个实现。
- `backend/data/notes.json` 是本机数据，已被 `.gitignore` 忽略；第一次 `notes add` 会自动创建。
- 余弦相似度显式校验维度：不同 embedding 模型 / 维度不一致会直接 `ValueError`，不再让 `zip` 静默截断。
- `retrieval/keyword.py` 是 W1 的简单基线，**冻结不改**；W7 的 BM25 / 混合检索 / rerank 全部新建模块，不重写它。
- 20 条评测问题 + hit@3 baseline 推迟到 W3/W7；现在 4 条便贴做评测没有意义。
