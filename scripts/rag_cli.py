# scripts/rag_cli.py
# CLI 薄入口：真正的逻辑在 backend/app，这里只负责把 backend 加进 sys.path。
# 运行（项目根目录，conda 环境 shiyi）：
#   python scripts/rag_cli.py notes list
#   python scripts/rag_cli.py notes add
#   python scripts/rag_cli.py ask

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.cli.main import main

if __name__ == "__main__":
    # 这一行：直接运行时执行 main()；被 import 时不执行
    main()
