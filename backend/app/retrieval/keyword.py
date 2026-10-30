# backend/app/retrieval/keyword.py
# 关键词检索：按共同词数量打分，再排序。纯函数，不读写文件。

from app.schemas.note import Note, ScoredNote
from app.utils.text import normalize_text


def score_note(note: Note, question: str) -> int:
    """简单版相似度：统计问题词与标题/内容/分类的交集词数。"""
    query = normalize_text(question)
    query_words = {word for word in query.split() if word}
    if not query_words:
        return 0

    haystack = normalize_text(
        f"{note.get('title', '')} {note.get('content', '')} {note.get('category', '')}"
    )
    note_words = set(haystack.split())
    # 两个集合的交集长度 = 有多少个相同的词
    return len(query_words & note_words)


def keyword_search(question: str, notes: list[Note]) -> list[ScoredNote]:
    """返回按关键词分数降序排列的便贴；分数为 0 的不保留。"""
    scored: list[ScoredNote] = []
    for note in notes:
        match_score = score_note(note, question)
        if match_score > 0:
            scored.append({
                "title": note.get("title", ""),
                "category": note.get("category", ""),
                "content": note.get("content", ""),
                "score": match_score,
            })
            # 这里后面的 "" 是指如果返回值没有，就给个默认值 ""

    # key=lambda ...：可以理解成逐个遍历 scored 里的 dict，
    # 先按 score 降序（负号翻转），分数相同再按标题升序
    return sorted(scored, key=lambda item: (-item["score"], item["title"].lower()))
