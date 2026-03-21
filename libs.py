import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def get_answer(prompt, history, query, model="gpt-4o-mini", temp=0.7):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [{"role": "system", "content": prompt}]
    if history:
        messages.append({"role": "system", "content": f"История диалога: {history}"})
    messages.append({"role": "user", "content": query})
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp
    )
    return response.choices[0].message.content
