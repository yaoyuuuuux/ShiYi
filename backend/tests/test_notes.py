# backend/tests/test_notes.py
# 纯函数测试：便贴参与 embedding 的文本。

import unittest

from app.notes.service import note_text


class NoteServiceTest(unittest.TestCase):
    def test_note_text_uses_title_and_content(self) -> None:
        note = {"title": "标题", "category": "运动", "content": "原文"}
        self.assertEqual(note_text(note), "标题 原文")

    def test_note_text_ignores_category(self) -> None:
        note = {"title": "标题", "category": "运动", "content": "原文"}
        self.assertNotIn("运动", note_text(note))


if __name__ == "__main__":
    unittest.main()
