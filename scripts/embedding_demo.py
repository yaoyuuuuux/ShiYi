# scripts/embedding_demo.py
# 学习用对比 demo：同一个问题，看关键词检索和 embedding 检索的排名差异。
# 运行（项目根目录，conda 环境 shiyi）：
#   python scripts/embedding_demo.py --probe   # 探针：确认模型名和维度
#   python scripts/embedding_demo.py           # 对比：关键词 vs embedding
#
# 真正的检索逻辑在 backend/app；这里只负责打印对比。

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import config
from app.clients.embedding import EmbeddingClient, EmbeddingError
from app.retrieval.keyword import keyword_search
from app.retrieval.semantic import embedding_search
from app.notes.repository import NotesError
from app.notes.service import list_notes
from app.schemas.note import ScoredNote
from app.utils.log import setup_logging

setup_logging()


def print_ranking(title: str, results: list[ScoredNote]) -> None:
    """打印一组排名。"""
    print(f"\n[{title}]")
    if not results:
        print("没有结果。")
        return
    for index, item in enumerate(results, start=1):
        print(f"{index}. [{item['category']}] {item['title']} | score={item['score']:.4f}")


def probe() -> None:
    """用一条短文本确认模型名、维度和 Key 是否可用。"""
    api_key = config.get_embedding_api_key()
    if api_key is None:
        print(f"提示：在项目根目录的 .env 里写一行 {config.EMBEDDING_KEY_ENV}=你的Key")
        return

    client = EmbeddingClient(api_key=api_key)
    try:
        vectors = client.embed(["深蹲膝盖疼怎么调"])
    except EmbeddingError as e:
        print(f"[{config.EMBEDDING_MODEL}] 失败：{e}")
        return

    vector = vectors[0]
    print(f"[{config.EMBEDDING_MODEL}] 成功")
    print(f"维度：{len(vector)}")
    print(f"前 5 个值：{vector[:5]}")


def main() -> None:
    try:
        notes = list_notes()
    except NotesError as e:
        print(f"读取便贴失败：{e}")
        return
    if not notes:
        print("当前没有便贴数据。")
        return

    api_key = config.get_embedding_api_key()
    if api_key is None:
        print(f"提示：在项目根目录的 .env 里写一行 {config.EMBEDDING_KEY_ENV}=你的Key")
        return

    default_question = "练腿的时候膝盖不舒服怎么办"
    question = input(f"请输入问题（回车默认：{default_question}）：").strip() or default_question
    print(f"\n[问题] {question}")

    keyword_results = keyword_search(question, notes)[: config.TOP_K]
    print_ranking("关键词打分", keyword_results)

    client = EmbeddingClient(api_key=api_key)
    try:
        embedding_results = embedding_search(question, notes, client)
    except EmbeddingError as e:
        print(f"embedding 调用失败：{e}")
        return
    print_ranking("Embedding 打分（余弦相似度）", embedding_results)


if __name__ == "__main__":
    if "--probe" in sys.argv:
        probe()
    else:
        main()
