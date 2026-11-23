# Optional OpenAI helper. Configure OPENAI_API_KEY in the hosting environment.

import os
import aiohttp


async def ai(query):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AI helper is disabled. Set OPENAI_API_KEY to enable it.")

    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 150,
        "temperature": 0.7,
    }
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        ) as response:
            data = await response.json(content_type=None)
            if response.status >= 400:
                detail = data.get("error", {}).get("message", "Unknown API error")
                raise RuntimeError(f"OpenAI API returned {response.status}: {detail}")
            return (data["choices"][0]["message"].get("content") or "").strip()


async def ask_ai(client, message_to_edit, message):
    parts = (message.text or "").split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        return await message_to_edit.edit("Please enter a question after /openai.")
    try:
        response = await ai(parts[1].strip())
        await message_to_edit.edit(response or "No response was returned.")
    except Exception as exc:
        await message_to_edit.edit(f"AI request failed: {exc}")
