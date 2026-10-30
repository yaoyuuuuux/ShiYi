# backend/app/cli/main.py
# 拾遗 CLI 统一入口：便贴管理 + 提问。
# 运行（项目根目录）：
#   python scripts/rag_cli.py notes list
#   python scripts/rag_cli.py notes add
#   python scripts/rag_cli.py ask
#   python scripts/rag_cli.py ask "练腿的时候膝盖不舒服怎么办"

import argparse

from app import config
from app.clients.embedding import EmbeddingClient, EmbeddingError
from app.clients.qwen import QwenClient, QwenError
from app.notes import service as note_service
from app.notes.repository import NotesError
from app.rag.pipeline import RagError, answer_question
from app.schemas.note import Note, ScoredNote
from app.utils.log import setup_logging


def print_notes(notes: list[Note]) -> None:
    """打印便贴列表。"""
    print(f"共 {len(notes)} 张便贴\n")
    for i, note in enumerate(notes, start=1):
        print(f"{i}. [{note['category']}] {note['title']}")
        print(f"   {note['content']}")
        print()
    # 不返回值给接收方，是直接打到屏幕上给人看的


def print_sources(sources: list[ScoredNote]) -> None:
    """先展示检索到的原文便贴。"""
    print("\n[检索到的原文]")
    for index, item in enumerate(sources, start=1):
        print(f"{index}. [{item['category']}] {item['title']} | score={item['score']:.4f}")
        print(f"   {item['content']}")


def cmd_notes_list() -> None:
    try:
        notes = note_service.list_notes()
    except NotesError as e:
        print(f"读取便贴失败：{e}")
        return
    if not notes:
        print("还没有便贴。用 `notes add` 记一条。")
        return
    print_notes(notes)


def cmd_notes_add(args: argparse.Namespace) -> None:
    title = (args.title or input("标题：")).strip()
    category = (args.category or input("分类（默认 生活）：")).strip() or "生活"
    content = (args.content or input("原文：")).strip()
    if not title or not content:
        print("标题和原文都不能为空。")
        return
    try:
        note = note_service.add_note(title=title, content=content, category=category)
    except ValueError as e:
        print(e)
        return
    except NotesError as e:
        print(f"保存便贴失败：{e}")
        return
    print(f"已记下：[{note['category']}] {note['title']}")


def cmd_ask(args: argparse.Namespace) -> None:
    if args.top_k <= 0:
        print("top-k 必须是正整数。")
        return

    try:
        notes = note_service.list_notes()
    except NotesError as e:
        print(f"读取便贴失败：{e}")
        return
    if not notes:
        print("还没有便贴。先 `notes add` 记一条。")
        return

    question = (args.question or input("请输入问题：")).strip()
    if not question:
        print("问题不能为空。")
        return
    print(f"\n[问题] {question}")

    embedding_key = config.get_embedding_api_key()
    if embedding_key is None:
        print(f"提示：在项目根目录的 .env 里写一行 {config.EMBEDDING_KEY_ENV}=你的Key")
        return
    qwen_key = config.get_qwen_api_key()
    if qwen_key is None:
        print(f"提示：在项目根目录的 .env 里写一行 {config.QWEN_KEY_ENV}=你的Key")
        return

    embedding_client = EmbeddingClient(api_key=embedding_key)
    qwen_client = QwenClient(api_key=qwen_key)

    try:
        result = answer_question(
            question,
            notes,
            embedding_client=embedding_client,
            qwen_client=qwen_client,
            top_k=args.top_k,
        )
    except (EmbeddingError, QwenError, RagError) as e:
        print(f"调用失败：{e}")
        return

    print_sources(result.sources)
    print("\n[回答]")
    print(result.answer)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shiyi", description="拾遗：个人知识口袋 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    notes_parser = subparsers.add_parser("notes", help="便贴管理")
    notes_sub = notes_parser.add_subparsers(dest="notes_command", required=True)
    notes_sub.add_parser("list", help="列出全部便贴")

    add_parser = notes_sub.add_parser("add", help="新增一条便贴")
    add_parser.add_argument("--title", help="标题；不传则交互输入")
    add_parser.add_argument("--category", help="分类，默认 生活")
    add_parser.add_argument("--content", help="原文；不传则交互输入")

    ask_parser = subparsers.add_parser("ask", help="提问 → 检索 → 回答")
    ask_parser.add_argument("question", nargs="?", help="问题；不传则交互输入")
    ask_parser.add_argument(
        "--top-k",
        type=int,
        default=config.TOP_K,
        help=f"取前几条，默认 {config.TOP_K}",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "notes":
        if args.notes_command == "list":
            cmd_notes_list()
        elif args.notes_command == "add":
            cmd_notes_add(args)
    elif args.command == "ask":
        cmd_ask(args)


if __name__ == "__main__":
    main()
