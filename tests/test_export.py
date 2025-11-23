import json
import tempfile
import unittest
from pathlib import Path

from gemini_chat.export import to_html, to_json, to_markdown, write_export
from gemini_chat.models import Conversation


def sample() -> Conversation:
    conv = Conversation(system_instruction="be brief")
    conv.add_user("hello")
    conv.add_model("hi there")
    return conv


class ExportTest(unittest.TestCase):
    def test_markdown_includes_roles_and_system(self):
        md = to_markdown(sample(), title="Demo")
        self.assertIn("# Demo", md)
        self.assertIn("**System:** be brief", md)
        self.assertIn("**You:**", md)
        self.assertIn("**Gemini:**", md)
        self.assertIn("hi there", md)

    def test_json_round_trips(self):
        data = json.loads(to_json(sample()))
        self.assertEqual(data["system_instruction"], "be brief")
        self.assertEqual(data["messages"][0]["text"], "hello")

    def test_html_escapes_and_labels(self):
        conv = Conversation()
        conv.add_user("<script>")
        out = to_html(conv)
        self.assertIn("&lt;script&gt;", out)
        self.assertNotIn("<script>", out)

    def test_write_export_chooses_format_by_extension(self):
        with tempfile.TemporaryDirectory() as d:
            for name, needle in [("c.md", "**You:**"), ("c.json", '"messages"'), ("c.html", "<!doctype html>")]:
                path = Path(d) / name
                fmt = write_export(sample(), path)
                self.assertEqual(fmt, name.split(".")[1])
                self.assertIn(needle, path.read_text())


if __name__ == "__main__":
    unittest.main()
