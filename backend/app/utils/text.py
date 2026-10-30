# backend/app/utils/text.py
# 文本预处理：小写 + 去标点，供关键词匹配使用。

import re


def normalize_text(text: str) -> str:
    """小写 + 把非单词字符换成空格，方便按词切分。"""
    return re.sub(r"[\W_]+", " ", text.lower()).strip()
