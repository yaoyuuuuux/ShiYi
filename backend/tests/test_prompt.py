# backend/tests/test_prompt.py
# 纯函数测试：Prompt 里必须带问题和原文。

import unittest

from app.rag.prompt import build_prompt


class PromptTest(unittest.TestCase):
    def test_prompt_contains_question_and_sources(self) -> None:
        sources = [
            {
                "title": "深蹲",
                "category": "运动",
                "content": "膝盖对准脚尖",
                "score": 0.9,
            }
        ]
        prompt = build_prompt("膝盖疼怎么办", sources)

        self.assertIn("膝盖疼怎么办", prompt)
        self.assertIn("深蹲", prompt)
        self.assertIn("膝盖对准脚尖", prompt)
        self.assertIn("只能依据", prompt)


if __name__ == "__main__":
    unittest.main()
