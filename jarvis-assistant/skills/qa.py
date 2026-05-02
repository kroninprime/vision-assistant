import os
from app.main import assistant

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def qa_skill(prompt: str) -> str:
    # Strip the keyword and ask OpenAI if configured
    if OpenAI and (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY".lower())):
        client = OpenAI()
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Answer concisely as a friendly assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=120,
            )
            return completion.choices[0].message.content
        except Exception:
            pass
    return "General knowledge: set OPENAI_API_KEY to enable live answers."


assistant.register("general qa", ["who", "what", "when", "where", "why", "how", "tell me"], qa_skill)
