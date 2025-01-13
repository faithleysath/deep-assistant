import os
from openai import OpenAI
base_path = os.path.dirname(os.path.realpath(__file__))
client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)


class Agent:
    def __init__(self, name):
        self.name = name
        self.prompt_file = os.path.join(base_path, 'agents', name, 'prompt.txt')
        self.prompt = self.get_prompt()

    def get_prompt(self):
        with open(self.prompt_file, 'r') as f:
            return f.read()