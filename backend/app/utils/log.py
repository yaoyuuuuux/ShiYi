# backend/app/utils/log.py
# 日志初始化：CLI 入口调用一次即可。

import logging


def setup_logging() -> None:
    """配置根日志器：时间 - 级别 - 消息。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
