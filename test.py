from openai import OpenAI

client = OpenAI(
    api_key="sk-c5ea9ba45f3f4fdbb55c2d6a32399a57",
    base_url="https://api.deepseek.com",
)

def send_messages(messages, tools={}):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    print(response)
    return response.choices[0].message
