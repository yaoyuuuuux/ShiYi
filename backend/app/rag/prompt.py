# backend/app/rag/prompt.py
# 把检索到的原文拼成 Prompt；约束模型只依据便贴回答。

from app.schemas.note import ScoredNote


def build_prompt(question: str, sources: list[ScoredNote]) -> str:
    """把检索结果拼成给聊天模型的 Prompt。"""
    blocks = []
    for index, item in enumerate(sources, start=1):
        blocks.append(
            f"【便贴 {index}】\n"
            f"标题：{item['title']}\n"
            f"分类：{item['category']}\n"
            f"原文：{item['content']}"
        )
    notes_text = "\n\n".join(blocks)

    return f"""你是用户的个人知识助手。下面是从用户自己的便贴中检索到的原文，按相关度从高到低排列。

{notes_text}

用户的问题：{question}

请遵守：
1. 先用一句话直接回答，不要绕弯子。
2. 只能依据上面的便贴回答，不要编造便贴里没有的信息。
3. 如果便贴不足以回答，就直说“你的便贴里没有直接答案”，并用标题指出最接近的一条。
4. 用中文，简短；不要复述整段原文。"""
