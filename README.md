# 拾遗 ShiYi

便贴一样的个人记忆口袋：随手记、模糊找、越用越厚。

- 语义检索：问题 ↔ 自己的原文，按相关度排序
- 模型用你自己的原文语境简短回答
- 每天闪卡推送一条旧便贴（W6/W8）

## 当前进度

W1 已完成并打标签 `W1`：命令行便贴 RAG —— 记便贴 / 列便贴 / 语义检索 / 取 top-k 原文 / Qwen 一句话回答。本阶段功能、目录结构和说明见 [CHANGELOG.md](CHANGELOG.md)。

## 目录结构

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
│   │   │   ├── qwen.py            # QwenClient：请求参数/响应解析
│   │   │   └── embedding.py       # EmbeddingClient：请求参数/响应解析
│   │   ├── retrieval/
│   │   │   ├── keyword.py         # 关键词打分/排序
│   │   │   └── semantic.py        # 向量检索：embedding + 余弦 + top-k
│   │   ├── notes/
│   │   │   ├── repository.py      # JSON 读写
│   │   │   └── service.py         # 增/查/分类筛选
│   │   ├── rag/
│   │   │   ├── pipeline.py        # 检索 → Prompt → 回答
│   │   │   └── prompt.py          # 拼 Prompt
│   │   ├── schemas/note.py        # Note / ScoredNote
│   │   └── utils/                 # text / log
│   ├── data/notes.json            # 本机便贴数据（不入库）
│   ├── tests/                     # 纯函数测试
│   └── requirements.txt           # requests / python-dotenv
├── scripts/
│   ├── rag_cli.py                 # CLI 薄入口
│   └── embedding_demo.py          # 关键词 vs embedding 对比
├── docs/                          # 产品 / 学习文档（仅本地，不入库）
├── CLAUDE.md
└── README.md
```

`scripts/` 只放入口和演示，不写业务逻辑；每个功能只在 `backend/app/` 里有一份实现。

## 环境

项目统一使用 conda 环境 `shiyi`（Python 3.12）：

```bash
conda activate shiyi
python -m pip install -r backend/requirements.txt
python -c "import sys; print(sys.executable)"   # 必须指向 .../envs/shiyi/python.exe
```

复制模板并填入自己的 Key：

```bash
cp .env.example .env
```

```text
QWEN_API_KEY=...
SILICONFLOW_API_KEY=...
```

## 运行

```bash
# 便贴
python scripts/rag_cli.py notes list
python scripts/rag_cli.py notes add

# 提问：检索原文 → Qwen 回答
python scripts/rag_cli.py ask "练腿的时候膝盖不舒服怎么办"

# 对比 demo：关键词 vs embedding
python scripts/embedding_demo.py
python scripts/embedding_demo.py --probe

# 测试（不调 API）
python -m unittest discover -s backend/tests -t backend -v
```

`backend/data/notes.json` 是本机数据，已被 `.gitignore` 忽略；第一次用 `notes add` 记一条就会自动创建。

## 下一步

W2：FastAPI + MySQL + 便贴 CRUD + 最薄前端壳。
