# backend/tests/test_http.py
# 通用 HTTP 层测试：用 mock 替代真实请求，不调 API。

import logging
import unittest
from unittest.mock import Mock, patch

import requests

from app.clients.http import HttpError, explain_http_error, post_json


class PostJsonTest(unittest.TestCase):
    def setUp(self) -> None:
        # 这些用例故意触发错误分支，屏蔽预期的 ERROR 日志
        logging.disable(logging.CRITICAL)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)

    def _post(self) -> dict:
        return post_json(
            "https://example.test/v1",
            headers={"Authorization": "Bearer x"},
            body={"input": "x"},
            service="test",
            key_env="TEST_KEY",
        )

    @patch("app.clients.http.requests.post")
    def test_success(self, mock_post: Mock) -> None:
        resp = Mock(status_code=200)
        resp.json.return_value = {"ok": True}
        mock_post.return_value = resp

        self.assertEqual(self._post(), {"ok": True})

    @patch("app.clients.http.requests.post")
    def test_401_mentions_key_env(self, mock_post: Mock) -> None:
        resp = Mock(status_code=401, text="unauthorized")
        mock_post.return_value = resp

        with self.assertRaises(HttpError) as ctx:
            self._post()
        self.assertIn("TEST_KEY", str(ctx.exception))

    @patch("app.clients.http.requests.post")
    def test_timeout_raises_http_error(self, mock_post: Mock) -> None:
        mock_post.side_effect = requests.exceptions.Timeout

        with self.assertRaises(HttpError):
            self._post()

    @patch("app.clients.http.requests.post")
    def test_invalid_json_raises_http_error(self, mock_post: Mock) -> None:
        resp = Mock(status_code=200)
        resp.json.side_effect = ValueError("not json")
        mock_post.return_value = resp

        with self.assertRaises(HttpError):
            self._post()


class ExplainHttpErrorTest(unittest.TestCase):
    def test_401_mentions_key_env(self) -> None:
        message = explain_http_error(401, "", service="test", key_env="TEST_KEY")
        self.assertIn("TEST_KEY", message)

    def test_500_says_server_side(self) -> None:
        message = explain_http_error(500, "", service="test", key_env="TEST_KEY")
        self.assertIn("服务端故障", message)


if __name__ == "__main__":
    unittest.main()
