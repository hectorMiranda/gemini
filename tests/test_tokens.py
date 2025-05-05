import unittest

from gemini_chat.models import Conversation
from gemini_chat.tokens import conversation_tokens, estimate_tokens


class TokensTest(unittest.TestCase):
    def test_empty_is_zero(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_monotonic(self):
        self.assertGreater(estimate_tokens("hello world foo"), estimate_tokens("hello"))

    def test_conversation_sums_messages(self):
        conv = Conversation(system_instruction="sys")
        conv.add_user("hello there")
        conv.add_model("general kenobi")
        total = conversation_tokens(conv)
        self.assertGreaterEqual(total, estimate_tokens("hello there"))
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
