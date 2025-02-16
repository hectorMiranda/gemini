import json
import unittest

from gemini_chat.client import GeminiClient
from gemini_chat.config import Config
from gemini_chat.errors import ApiError
from gemini_chat.models import Conversation
from tests.support import FakeTransport

OK = (
    200,
    json.dumps({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}).encode(),
)
TRANSIENT = (503, b'{"error":{"message":"unavailable"}}')


def conv():
    c = Conversation()
    c.add_user("hi")
    return c


class RetryTest(unittest.TestCase):
    def setUp(self):
        self.config = Config(api_key="k", retries=2)

    def test_retries_then_succeeds(self):
        t = FakeTransport([TRANSIENT, OK])
        client = GeminiClient(self.config, transport=t, sleep=lambda _s: None)
        result = client.generate(conv())
        self.assertEqual(result.text, "ok")
        self.assertEqual(len(t.calls), 2)

    def test_gives_up_after_retries(self):
        t = FakeTransport([TRANSIENT, TRANSIENT, TRANSIENT])
        client = GeminiClient(self.config, transport=t, sleep=lambda _s: None)
        with self.assertRaises(ApiError):
            client.generate(conv())
        self.assertEqual(len(t.calls), 3)  # retries=2 -> 3 attempts


if __name__ == "__main__":
    unittest.main()
