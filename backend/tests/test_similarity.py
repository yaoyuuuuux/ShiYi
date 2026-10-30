# backend/tests/test_similarity.py
# 纯函数测试：余弦相似度，不需要 API Key。

import unittest

from app.retrieval.semantic import cosine_similarity


class CosineSimilarityTest(unittest.TestCase):
    def test_same_direction(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1, 2, 3], [2, 4, 6]), 1.0)

    def test_orthogonal(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_zero_vector(self) -> None:
        self.assertEqual(cosine_similarity([0, 0], [1, 2]), 0.0)

    def test_dimension_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            cosine_similarity([1, 2, 3], [1, 2])


if __name__ == "__main__":
    unittest.main()
