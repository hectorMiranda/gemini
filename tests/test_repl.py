import io
import unittest

from gemini_chat.config import Config
from gemini_chat.repl import Repl
from tests.support import FakeClient


def make_repl(replies=None):
    out = io.StringIO()
    repl = Repl(Config(api_key="k"), client=FakeClient(replies or ["hi!"]), out=out)
    return repl, out


class ReplTest(unittest.TestCase):
    def test_chat_appends_user_and_model_turns(self):
        repl, out = make_repl(["hello back"])
        repl.handle("hello")
        roles = [m.role.value for m in repl.conversation.messages]
        self.assertEqual(roles, ["user", "model"])
        self.assertIn("hello back", out.getvalue())

    def test_new_command_clears_history(self):
        repl, _ = make_repl()
        repl.handle("hi")
        repl.handle("/new")
        self.assertEqual(repl.conversation.messages, [])

    def test_exit_stops_running(self):
        repl, _ = make_repl()
        repl.handle("/exit")
        self.assertFalse(repl.running)

    def test_model_command_switches_model(self):
        repl, out = make_repl()
        repl.handle("/model gemini-1.5-pro")
        self.assertEqual(repl.config.model, "gemini-1.5-pro")
        self.assertIn("gemini-1.5-pro", out.getvalue())

    def test_unknown_command(self):
        repl, out = make_repl()
        repl.handle("/frobnicate")
        self.assertIn("unknown command", out.getvalue())


if __name__ == "__main__":
    unittest.main()
