# backend/app/rag/pipeline.py
# RAG 编排：检索 top-k -> 拼 Prompt -> 调聊天模型。

from dataclasses import dataclass

from app import config
from app.clients.embedding import EmbeddingClient
from app.clients.qwen import QwenClient
from app.rag.prompt import build_prompt
from app.retrieval.semantic import embedding_search
from app.schemas.note import Note, ScoredNote


class RagError(Exception):
    """RAG 流程无法继续时抛出。"""


@dataclass(frozen=True)
class AnswerResult:
    """一次问答的结果：命中的原文 + 模型回答。"""

    sources: list[ScoredNote]
    answer: str


def answer_question(
    question: str,
    notes: list[Note],
    *,
    embedding_client: EmbeddingClient,
    qwen_client: QwenClient,
    top_k: int = config.TOP_K,
) -> AnswerResult:
    """检索原文，拼 Prompt，返回模型回答。"""
    if not notes:
        raise RagError("没有便贴数据")

    sources = embedding_search(question, notes, embedding_client, top_k)
    if not sources:
        raise RagError("没有检索到相关便贴")

    prompt = build_prompt(question, sources)
    answer = qwen_client.ask(prompt)
    return AnswerResult(sources=sources, answer=answer)
