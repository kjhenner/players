import argparse
import os
import difflib
import time
from typing import List, Dict

import dotenv
import openai


def load_api_key() -> str:
    """
    Loads OpenAPI key from .env file.

    Returns:
        str: The API key.
    """
    dotenv.load_dotenv()
    return os.getenv("OPENAI_KEY")


def call_chat_text_completion(messages: List[Dict[str, str]]) -> str:
    """
    Calls the OpenAI chat text completion API end point.

    Args:
        messages (list[str]): The message to send.

    Returns:
        str: The response from the API.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()


def load_prompt_text(prompt_name: str) -> str:
    """
    Loads the prompt text from a file in the prompts folder.
    Args:
        prompt_name (str): The name of the prompt file.

    Returns:
        str: The prompt text.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    system_message_path = os.path.join(base_dir, "prompts", prompt_name)
    with open(system_message_path) as f:
        return f.read()


def main(args: argparse.Namespace) -> None:
    """
    Main function that encapsulates the workflow.

    Args:
        args (argparse.Namespace): CLI arguments namespace.
    """
    if not openai.api_key:
        openai.api_key = load_api_key()

    lines = []
    play = PlayerAgent("play.txt")
    while True:
        retries = 0
        while retries <= 3:
            try:
                time.sleep(0.5)
                next = play.get_next_line(lines)
                print(next)
                lines.append(next)
                break
            except openai.error.RateLimitError:
                print("Rate limit error, retrying...")
                time.sleep(1)
                continue


class PlayerAgent:

    def __init__(self, system_message_name: str):
        self.system_prompt_message = {
            "role": "system",
            "content": load_prompt_text(system_message_name),
        }

    def get_next_line(self, lines: List[str]) -> str:
        messages = [
            self.system_prompt_message,
            {
                "role": "user",
                "content": "\n\n".join(lines)
            }
        ]
        return call_chat_text_completion(messages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)