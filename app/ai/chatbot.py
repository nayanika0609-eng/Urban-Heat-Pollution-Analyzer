import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def ask_ai(chat_history, question, context=None):
    system_prompt = """
You are an AI assistant focused on sustainability, climate change,
urban planning, and environmental science.

You can answer general sustainability questions and also explain
project-specific results when context is provided.
Be clear and concise.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add previous conversation (memory)
    for msg in chat_history:
        messages.append(msg)

    # Add project context (optional)
    if context:
        messages.append({
            "role": "user",
            "content": f"Project context:\n{context}"
        })

    # Add current question
    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content
