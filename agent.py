import os
from openai import OpenAI

base_path = os.path.dirname(os.path.realpath(__file__))

client = OpenAI(
    api_key="sk-c5ea9ba45f3f4fdbb55c2d6a32399a57",
    base_url="https://api.deepseek.com",
)

async def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    print(response)
    return response.choices[0].message

class Agent:
    def __init__(self, name):
        self.name = name
        self.prompt_file = os.path.join(base_path, 'agents', name, 'prompt.txt')
        self.prompt = self.get_prompt()

    def get_prompt(self):
        with open(self.prompt_file, 'r') as f:
            return f.read()