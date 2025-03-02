import unittest

from gemini_chat.export import to_markdown
from gemini_chat.models import Conversation


class ExportTest(unittest.TestCase):
    def test_markdown_includes_roles_and_system(self):
        conv = Conversation(system_instruction="be brief")
        conv.add_user("hello")
        conv.add_model("hi there")
        md = to_markdown(conv, title="Demo")
        self.assertIn("# Demo", md)
        self.assertIn("**System:** be brief", md)
        self.assertIn("**You:**", md)
        self.assertIn("**Gemini:**", md)
        self.assertIn("hello", md)
        self.assertIn("hi there", md)


if __name__ == "__main__":
    unittest.main()
