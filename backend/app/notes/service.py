# backend/app/notes/service.py
# 便贴业务层：增、查、按分类筛、拼 embedding 文本。

from app.notes import repository
from app.schemas.note import Note


def filter_by_category(notes: list[Note], category: str | None = None) -> list[Note]:
    """按分类筛选；category 为空时返回原列表。"""
    if category is None:
        return notes
    # 列表推导：一行筛出指定分类
    return [note for note in notes if note.get("category") == category]


def list_notes(category: str | None = None) -> list[Note]:
    """返回全部便贴；传 category 时只返回该分类。"""
    notes = repository.load_notes()
    return filter_by_category(notes, category)


def has_note(notes: list[Note], title: str) -> bool:
    """按标题查重。"""
    return any(note.get("title") == title for note in notes)


def add_note(title: str, content: str, category: str = "生活") -> Note:
    """新增一条便贴并写回文件；标题重复时抛 ValueError。"""
    notes = repository.load_notes()
    if has_note(notes, title):
        raise ValueError(f"已经有同名便贴：{title}")
    note: Note = {"title": title, "category": category, "content": content}
    notes.append(note)
    repository.save_notes(notes)
    return note


def note_text(note: Note) -> str:
    """一条便贴参与 embedding 的文本：标题 + 原文；分类不进来。"""
    return f"{note.get('title', '')} {note.get('content', '')}"
