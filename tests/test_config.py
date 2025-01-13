import tempfile
import unittest
from pathlib import Path

from gemini_chat.config import Config


class ConfigTest(unittest.TestCase):
    def _write(self, text: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False)
        tmp.write(text)
        tmp.close()
        return Path(tmp.name)

    def test_file_values_loaded(self):
        path = self._write('model = "gemini-1.5-pro"\ntemperature = 0.2\nretries = 5\n')
        cfg = Config.load(path=path, env={})
        self.assertEqual(cfg.model, "gemini-1.5-pro")
        self.assertEqual(cfg.temperature, 0.2)
        self.assertEqual(cfg.retries, 5)

    def test_env_overrides_file(self):
        path = self._write('model = "gemini-1.5-pro"\n')
        cfg = Config.load(path=path, env={"GEMINI_MODEL": "gemini-1.5-flash", "GEMINI_API_KEY": "k"})
        self.assertEqual(cfg.model, "gemini-1.5-flash")
        self.assertEqual(cfg.api_key, "k")

    def test_defaults_when_no_file(self):
        cfg = Config.load(path=Path("/nonexistent/x.toml"), env={})
        self.assertEqual(cfg.model, "gemini-1.5-flash")
        self.assertEqual(cfg.retries, 2)


if __name__ == "__main__":
    unittest.main()
