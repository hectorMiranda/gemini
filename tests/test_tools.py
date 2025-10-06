import json
import unittest

from gemini_chat.client import GeminiClient
from gemini_chat.config import Config
from gemini_chat.models import Conversation
from gemini_chat.tools import CALCULATOR, to_request
from tests.support import FakeTransport

OK = (200, json.dumps({"candidates": [{"content": {"parts": [{"text": "4"}]}}]}).encode())


class ToolsTest(unittest.TestCase):
    def test_to_request_shape(self):
        req = to_request([CALCULATOR])
        self.assertEqual(req[0]["functionDeclarations"][0]["name"], "calculate")

    def test_client_includes_tools_in_body(self):
        t = FakeTransport([OK])
        client = GeminiClient(Config(api_key="k", retries=0), transport=t, tools=[CALCULATOR])
        conv = Conversation()
        conv.add_user("2+2")
        client.generate(conv)
        body = t.last_body_json
        self.assertIn("tools", body)
        self.assertEqual(body["tools"][0]["functionDeclarations"][0]["name"], "calculate")

    def test_no_tools_means_no_field(self):
        t = FakeTransport([OK])
        client = GeminiClient(Config(api_key="k", retries=0), transport=t)
        conv = Conversation()
        conv.add_user("hi")
        client.generate(conv)
        self.assertNotIn("tools", t.last_body_json)


if __name__ == "__main__":
    unittest.main()
