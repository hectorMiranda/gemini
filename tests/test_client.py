import json
import unittest

from gemini_chat.client import GeminiClient
from gemini_chat.config import Config
from gemini_chat.errors import AuthError, RateLimitError
from gemini_chat.models import Conversation
from tests.support import FakeTransport


def ok_response(text="hi there", prompt=3, out=2):
    return (
        200,
        json.dumps(
            {
                "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
                "usageMetadata": {
                    "promptTokenCount": prompt,
                    "candidatesTokenCount": out,
                    "totalTokenCount": prompt + out,
                },
            }
        ).encode(),
    )


class ClientTest(unittest.TestCase):
    def setUp(self):
        # retries=0 so a single error response maps directly (no backoff loop).
        self.config = Config(api_key="test-key", model="gemini-1.5-flash", retries=0)

    def test_generate_parses_text_and_usage(self):
        t = FakeTransport([ok_response("hello", prompt=5, out=7)])
        client = GeminiClient(self.config, transport=t)
        conv = Conversation()
        conv.add_user("hi")
        result = client.generate(conv)
        self.assertEqual(result.text, "hello")
        self.assertEqual(result.total_tokens, 12)
        self.assertEqual(result.finish_reason, "STOP")

    def test_request_url_and_body(self):
        t = FakeTransport([ok_response()])
        self.config.system_instruction = "be terse"
        client = GeminiClient(self.config, transport=t)
        conv = Conversation()
        conv.add_user("hi")
        client.generate(conv)
        url = t.calls[0]["url"]
        self.assertIn("models/gemini-1.5-flash:generateContent", url)
        self.assertIn("key=test-key", url)
        body = t.last_body_json
        self.assertEqual(body["systemInstruction"]["parts"][0]["text"], "be terse")

    def test_rate_limit_maps_to_error(self):
        t = FakeTransport([(429, b'{"error":{"message":"quota exceeded"}}')])
        client = GeminiClient(self.config, transport=t)
        conv = Conversation()
        conv.add_user("hi")
        with self.assertRaises(RateLimitError):
            client.generate(conv)

    def test_auth_error(self):
        t = FakeTransport([(403, b'{"error":{"message":"bad key"}}')])
        client = GeminiClient(self.config, transport=t)
        conv = Conversation()
        conv.add_user("hi")
        with self.assertRaises(AuthError):
            client.generate(conv)


if __name__ == "__main__":
    unittest.main()
