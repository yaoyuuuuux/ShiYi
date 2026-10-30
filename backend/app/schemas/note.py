# backend/app/schemas/note.py
# 便贴的数据形状。W2 接 Pydantic 时可以替换成 BaseModel。

from typing import TypedDict


class Note(TypedDict):
    title: str
    category: str
    content: str


class ScoredNote(TypedDict):
    title: str
    category: str
    content: str
    score: float
