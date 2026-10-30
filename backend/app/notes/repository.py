# backend/app/notes/repository.py
# 便贴的持久化层：只负责 JSON 读写，不掺业务逻辑。

import json
import logging
from pathlib import Path

from app import config
from app.schemas.note import Note


class NotesError(Exception):
    """便贴文件读写失败时抛出，消息是给人看的中文原因。"""


def load_notes(path: Path = config.NOTES_FILE) -> list[Note]:
    """读取全部便贴；文件不存在返回空列表，内容坏了抛 NotesError。"""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logging.exception("读取便贴文件失败：%s", path)
        raise NotesError(f"便贴文件读取失败：{path}") from e
    if not isinstance(payload, list):
        raise NotesError(f"便贴文件格式不对，应该是 JSON 数组：{path}")
    return payload


def save_notes(notes: list[Note], path: Path = config.NOTES_FILE) -> None:
    """把全部便贴写回 JSON；先写临时文件再替换，避免写一半坏掉。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        tmp_path.replace(path)
    except OSError as e:
        logging.exception("写入便贴文件失败：%s", path)
        raise NotesError(f"便贴文件写入失败：{path}") from e
