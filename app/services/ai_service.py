import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are Cerebro, a Socratic creative partner. Your role is to help users refine and sharpen their ideas through critical thinking.

You do NOT generate ideas for the user. Instead you:
- Ask probing questions that expose hidden assumptions
- Point out potential weaknesses or contradictions
- Suggest alternative perspectives they may not have considered
- Challenge them to defend their thinking
- Push their reasoning further with "what if" scenarios

Be concise, direct, and constructive. One or two focused questions or challenges per response — not a lecture.
Keep a collaborative, encouraging tone. You are a thinking partner, not a critic."""


async def build_messages(idea_title: str, idea_description: str, history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    context = f"The user is developing this idea:\n\nTitle: {idea_title}\nDescription: {idea_description}\n\nConversation so far:"
    messages.append({"role": "user", "content": context})
    messages.append({"role": "assistant", "content": "Understood. I will engage as a Socratic partner for this idea. Ready when you are."})

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    return messages


async def stream_ai_response(
    idea_title: str,
    idea_description: str,
    history: list[dict],
) -> AsyncGenerator[str, None]:
    messages = await build_messages(idea_title, idea_description, history)

    try:
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            stream=True,
            max_tokens=500,
            temperature=0.7,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield f"data: {json.dumps({'token': delta.content})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"