# backend/app/clients/qwen.py
# Qwen 聊天模型客户端：只负责请求参数和响应结构，HTTP 细节交给 http.py。

import logging

from app import config
from app.clients.http import bearer_headers, post_json


class QwenError(Exception):
    """Qwen 调用失败时抛出，消息是给人看的中文原因。

    对照 Java：extends Exception，自定义一个业务异常。
    """


class QwenClient:
    """Qwen 聊天客户端；创建时把配置装进对象，之后反复调用。"""

    def __init__(self, api_key: str, model: str = config.QWEN_MODEL) -> None:
        self.api_key = api_key
        self.model = model

    def ask(self, prompt: str) -> str:
        """发一次对话请求，返回模型回答的文本；失败抛 QwenError。"""
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = post_json(
            config.QWEN_BASE_URL,
            headers=bearer_headers(self.api_key),
            body=body,
            service="Qwen",
            key_env=config.QWEN_KEY_ENV,
            error_cls=QwenError,
        )

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logging.exception("Qwen 返回格式不符合预期")
            raise QwenError("Qwen 返回的内容看不懂，可能是服务端临时故障") from e
