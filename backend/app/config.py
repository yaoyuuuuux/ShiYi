# backend/app/config.py
# 全局配置：路径、Key、模型名、检索参数。
# 只在这里读 .env；其他模块通过 config 取，不自己 load_dotenv。

import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent          # backend/app
BACKEND_DIR = APP_DIR.parent                       # backend
PROJECT_ROOT = BACKEND_DIR.parent                  # ShiYi/
DATA_DIR = BACKEND_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.json"

# 项目根目录的 .env；找不到就跳过，不报错
load_dotenv(PROJECT_ROOT / ".env")

# Qwen 聊天模型
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen3.8-27b"
QWEN_LIGHT_MODEL = "qwen3.8-flash"
QWEN_KEY_ENV = "QWEN_API_KEY"

# embedding（硅基流动托管的 BGE-M3，OpenAI 兼容接口）
EMBEDDING_BASE_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
EMBEDDING_KEY_ENV = "SILICONFLOW_API_KEY"

# 检索 / HTTP
TOP_K = 3
HTTP_TIMEOUT = 30

# 国内服务直连；Windows 系统代理没关干净时，requests 会误走代理
NO_PROXY = {"http": None, "https": None}


def get_qwen_api_key() -> str | None:
    """从环境变量取 Qwen Key；没配置返回 None。"""
    return os.getenv(QWEN_KEY_ENV)


def get_embedding_api_key() -> str | None:
    """从环境变量取硅基流动 Key；没配置返回 None。"""
    return os.getenv(EMBEDDING_KEY_ENV)
