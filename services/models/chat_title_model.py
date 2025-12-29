from dotenv import load_dotenv
from pydantic_ai import ModelSettings, Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

SYSTEM_PROMPT = """
Generate a 2–6 word title summarizing the user’s message.
Title case. No punctuation. No emojis. Output only the title.
"""

model_name = "google/gemma-3n-e4b-it"
model = OpenRouterModel(
    model_name,
    provider="openrouter",
    settings=ModelSettings(extra_body={"type": "json_object", "reasoning": {"enabled": False}})
)

agent = Agent[None, str](
    model,
    output_type=str,
    system_prompt=SYSTEM_PROMPT
)

async def generate_chat_title(user_message: str) -> str:
    try:
        response = await agent.run(user_prompt=user_message[:100])
        return response.output.strip()
    except Exception as e:
        print("Failed to generate chat title", e)
        return "Chat"