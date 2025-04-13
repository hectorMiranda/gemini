import io
import unittest

from gemini_chat.cli import run_once
from gemini_chat.config import Config
from tests.support import FakeClient


class CliTest(unittest.TestCase):
    def test_run_once_streams_reply(self):
        out = io.StringIO()
        rc = run_once(Config(api_key="k"), "hello", client=FakeClient(["hello world"]), out=out)
        self.assertEqual(rc, 0)
        self.assertIn("hello world", out.getvalue())

    def test_run_once_non_stream(self):
        out = io.StringIO()
        cfg = Config(api_key="k", stream=False)
        rc = run_once(cfg, "hi", client=FakeClient(["pong"]), out=out)
        self.assertEqual(rc, 0)
        self.assertIn("pong", out.getvalue())


if __name__ == "__main__":
    unittest.main()
