# backend/tests/test_keyword.py
# 纯函数测试：关键词打分、排序、分类筛选。

import unittest

from app.retrieval.keyword import keyword_search, score_note
from app.notes.service import filter_by_category

NOTES = [
    {
        "title": "深蹲膝盖疼怎么调",
        "category": "运动",
        "content": "膝盖对准脚尖，不要内扣。",
    },
    {
        "title": "红烧肉去油技巧",
        "category": "生活",
        "content": "先煎出油再炖。",
    },
]


class KeywordTest(unittest.TestCase):
    def test_score_note_hit(self) -> None:
        # 关键词法按空格切词，中文要整句命中
        self.assertGreater(score_note(NOTES[0], "深蹲膝盖疼怎么调"), 0)

    def test_partial_chinese_query_does_not_match(self) -> None:
        # 半句「深蹲膝盖疼」不会命中整句标题，这是关键词法的局限
        self.assertEqual(score_note(NOTES[0], "深蹲膝盖疼"), 0)

    def test_score_note_miss(self) -> None:
        self.assertEqual(score_note(NOTES[1], "深蹲膝盖疼怎么调"), 0)

    def test_keyword_search_sorted(self) -> None:
        results = keyword_search("深蹲膝盖疼怎么调", NOTES)
        self.assertEqual(results[0]["title"], "深蹲膝盖疼怎么调")

    def test_filter_by_category(self) -> None:
        self.assertEqual(len(filter_by_category(NOTES, "运动")), 1)
        self.assertEqual(filter_by_category(NOTES, None), NOTES)


if __name__ == "__main__":
    unittest.main()
