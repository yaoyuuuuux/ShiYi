# backend/app/clients/http.py
# 通用 HTTP 层：POST JSON、网络/状态码/JSON 错误统一处理、错误翻译。
# qwen.py / embedding.py 只负责各自的请求参数和响应结构。

import logging

import requests

from app import config


class HttpError(Exception):
    """HTTP 调用失败时抛出，消息是给人看的中文原因。"""


def bearer_headers(api_key: str) -> dict[str, str]:
    """构造 Bearer 认证头。"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def explain_http_error(
    status_code: int,
    body_text: str,
    *,
    service: str,
    key_env: str,
) -> str:
    """把状态码翻译成终端用户能看懂的中文原因。"""
    if status_code == 401:
        return f"{service} API Key 无效，请检查 .env 里的 {key_env}"
    if status_code == 429:
        return f"{service} 请求太频繁或额度用尽，稍后再试"
    if status_code == 400:
        return f"{service} 请求参数不被接受（HTTP 400）：{body_text[:200]}"
    if "arrearage" in body_text.lower():
        return f"{service} 账户余额不足，请充值后再试"
    if status_code >= 500:
        return f"{service} 服务端故障，不是你的问题，稍后再试"
    return f"{service} 调用失败（HTTP {status_code}），详细原因见上面的日志"


def post_json(
    url: str,
    *,
    headers: dict[str, str],
    body: dict,
    service: str,
    key_env: str,
    error_cls: type[Exception] = HttpError,
    timeout: int = config.HTTP_TIMEOUT,
) -> dict:
    """POST JSON，统一处理网络层、状态码和 JSON 解析。

    响应体的业务结构由调用方解析（Qwen 的 choices / embedding 的 data）。
    """
    # 第一道防线：网络层错误（超时、断网）
    try:
        resp = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=timeout,
            proxies=config.NO_PROXY,
        )
    except requests.exceptions.Timeout as e:
        logging.exception("%s 请求超时", service)
        raise error_cls(f"{service} 等了 {timeout} 秒没有回应，请检查网络后重试") from e
    except requests.exceptions.ConnectionError as e:
        logging.exception("连接 %s 失败", service)
        raise error_cls(f"{service} 连不上服务器，请检查网络") from e

    # 第二道防线：HTTP 状态码不是 200
    if resp.status_code != 200:
        logging.error("%s 返回 HTTP %s：%s", service, resp.status_code, resp.text)
        raise error_cls(
            explain_http_error(
                resp.status_code,
                resp.text,
                service=service,
                key_env=key_env,
            )
        )

    # 第三道防线：状态码 200 但响应体不是合法 JSON
    try:
        return resp.json()
    except ValueError as e:
        logging.exception("%s 返回内容不是合法 JSON", service)
        raise error_cls(f"{service} 返回的内容看不懂，可能是服务端临时故障") from e
