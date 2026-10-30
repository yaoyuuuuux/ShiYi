# backend/app/retrieval/semantic.py
# 向量检索：把问题和便贴编码成向量，算余弦，排序取 top-k。

import math

from app import config
from app.clients.embedding import EmbeddingClient
from app.notes.service import note_text
from app.schemas.note import Note, ScoredNote


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度；维度不同直接报错，避免 zip 静默截断。"""
    if len(a) != len(b):
        raise ValueError(
            f"向量维度不一致：{len(a)} vs {len(b)}；"
            "入库和查询必须使用同一个 embedding 模型"
        )

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        # zip(a, b) 同位置配对：a[0]、b[0] 一组，依次放进 x、y
        dot += x * y
        norm_a += x * x
        norm_b += y * y

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def embedding_search(
    question: str,
    notes: list[Note],
    client: EmbeddingClient,
    top_k: int = config.TOP_K,
) -> list[ScoredNote]:
    """用 embedding + 余弦给便贴打分，返回前 top_k 条。"""
    note_vectors = client.embed([note_text(note) for note in notes])
    question_vector = client.embed([question])[0]

    scored: list[ScoredNote] = []
    for note, vector in zip(notes, note_vectors):
        score = cosine_similarity(question_vector, vector)
        scored.append({
            "title": note.get("title", ""),
            "category": note.get("category", ""),
            "content": note.get("content", ""),
            "score": score,
        })

    # 先按分数降序，分数相同再按标题升序
    return sorted(scored, key=lambda item: (-item["score"], item["title"].lower()))[:top_k]
