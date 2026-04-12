import unittest

from gemini_chat.render import render


class RenderTest(unittest.TestCase):
    def test_strips_markers_without_color(self):
        out = render("**bold** and `code` and *em*", color=False)
        self.assertEqual(out, "bold and code and em")

    def test_heading_without_color(self):
        self.assertEqual(render("# Title", color=False), "Title")

    def test_bold_emits_ansi_with_color(self):
        out = render("**hi**", color=True)
        self.assertIn("\033[1m", out)
        self.assertIn("hi", out)

    def test_code_fence_indents_and_drops_fences(self):
        text = "```python\nprint(1)\n```"
        out = render(text, color=False)
        self.assertEqual(out, "    print(1)")

    def test_inline_code_colored(self):
        out = render("use `x`", color=True)
        self.assertIn("\033[36m", out)

    def test_asterisks_inside_code_are_literal(self):
        # Regression: markup inside an inline-code span must not be styled.
        self.assertEqual(render("`a*b*c`", color=False), "a*b*c")
        colored = render("`a*b*c`", color=True)
        self.assertIn("a*b*c", colored)
        self.assertNotIn("\033[3m", colored)  # no italic applied inside code


if __name__ == "__main__":
    unittest.main()
