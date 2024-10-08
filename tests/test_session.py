import tempfile
import unittest
from pathlib import Path

from gemini_chat import session
from gemini_chat.models import Conversation, Part


class SessionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_round_trip_preserves_messages(self):
        conv = Conversation(system_instruction="be brief")
        conv.add_user("hello")
        conv.add_model("hi")
        session.save_session("chat1", conv, directory=self.dir)

        loaded = session.load_session("chat1", directory=self.dir)
        self.assertEqual(loaded.system_instruction, "be brief")
        self.assertEqual([m.text_content for m in loaded.messages], ["hello", "hi"])

    def test_round_trip_preserves_binary_part(self):
        conv = Conversation()
        conv.add_user("see this", parts=[Part(text="see this"), Part(mime_type="image/png", data=b"\x89PNG\x01\x02")])
        session.save_session("img", conv, directory=self.dir)
        loaded = session.load_session("img", directory=self.dir)
        self.assertEqual(loaded.messages[0].parts[1].data, b"\x89PNG\x01\x02")

    def test_list_and_delete(self):
        conv = Conversation()
        conv.add_user("x")
        session.save_session("a", conv, directory=self.dir)
        session.save_session("b", conv, directory=self.dir)
        self.assertEqual(session.list_sessions(self.dir), ["a", "b"])
        self.assertTrue(session.delete_session("a", directory=self.dir))
        self.assertEqual(session.list_sessions(self.dir), ["b"])

    def test_load_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            session.load_session("nope", directory=self.dir)

    def test_unsafe_name_is_sanitized(self):
        conv = Conversation()
        conv.add_user("x")
        path = session.save_session("my chat/../etc", conv, directory=self.dir)
        self.assertTrue(path.name.endswith(".json"))
        self.assertNotIn("/", path.stem)


if __name__ == "__main__":
    unittest.main()
