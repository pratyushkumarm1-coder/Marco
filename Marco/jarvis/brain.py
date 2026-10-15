from openai import OpenAI
from .config import OPENAI_API_KEY, GPT_MODEL, SYSTEM_PROMPT
from .memory import get_history, save_message, log_command


client = OpenAI(api_key=OPENAI_API_KEY)


def think(user_input: str) -> str:
    history = get_history()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    save_message("user", user_input)

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500,
    )

    reply = response.choices[0].message.content.strip()

    save_message("assistant", reply)

    return reply


def think_with_tools(user_input: str) -> str:
    return think(user_input)
