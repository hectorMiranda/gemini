import base64
import unittest

from gemini_chat.models import Conversation, Message, Part, Role


class ModelsTest(unittest.TestCase):
    def test_text_message_to_wire(self):
        m = Message.text(Role.USER, "hello")
        self.assertEqual(m.to_wire(), {"role": "user", "parts": [{"text": "hello"}]})

    def test_inline_binary_part_is_base64(self):
        part = Part(mime_type="image/png", data=b"\x89PNG")
        wire = part.to_wire()
        self.assertEqual(wire["inlineData"]["mimeType"], "image/png")
        self.assertEqual(base64.b64decode(wire["inlineData"]["data"]), b"\x89PNG")

    def test_conversation_contents_order(self):
        c = Conversation()
        c.add_user("hi")
        c.add_model("hello there")
        contents = c.to_contents()
        self.assertEqual([m["role"] for m in contents], ["user", "model"])

    def test_text_content_joins_parts(self):
        m = Message(role=Role.MODEL, parts=[Part(text="a"), Part(text="b")])
        self.assertEqual(m.text_content, "ab")


if __name__ == "__main__":
    unittest.main()
