"""Example: ask Gemini one question using the library directly.

    GEMINI_API_KEY=... python examples/oneshot.py
"""

from gemini_chat.client import GeminiClient
from gemini_chat.config import Config
from gemini_chat.models import Conversation


def main() -> None:
    client = GeminiClient(Config.load())
    conv = Conversation()
    conv.add_user("Say hello in three languages.")
    print(client.generate(conv).text)


if __name__ == "__main__":
    main()
