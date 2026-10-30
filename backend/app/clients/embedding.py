# backend/app/clients/embedding.py
# OpenAI 兼容的 embedding 客户端：只负责请求参数和响应结构，HTTP 细节交给 http.py。

import logging

from app import config
from app.clients.http import bearer_headers, post_json


class EmbeddingError(Exception):
    """embedding 调用失败时抛出的统一异常，消息是给人看的中文原因。"""


class EmbeddingClient:
    """把一批文本转成向量；返回顺序和输入一致。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = config.EMBEDDING_BASE_URL,
        model: str = config.EMBEDDING_MODEL,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """把一批文本转成向量，返回顺序和输入一致。"""
        body = {"model": self.model, "input": texts}
        data = post_json(
            self.base_url,
            headers=bearer_headers(self.api_key),
            body=body,
            service="embedding",
            key_env=config.EMBEDDING_KEY_ENV,
            error_cls=EmbeddingError,
        )

        try:
            items = data["data"]
            # 批量请求时 API 可能乱序返回；按 index 排序后，
            # zip(notes, vectors) 才能保证第 i 条便贴配第 i 个向量。
            if items and "index" in items[0]:
                items = sorted(items, key=lambda item: item["index"])
            return [item["embedding"] for item in items]
        except (KeyError, TypeError, ValueError) as e:
            logging.exception("embedding 返回格式不符合预期")
            raise EmbeddingError("embedding 返回的内容看不懂，可能是服务端临时故障") from e
