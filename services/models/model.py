from datetime import datetime
import json
import traceback

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelSettings, TextPart, AgentRunResultEvent, PartStartEvent, PartDeltaEvent, \
    TextPartDelta, RunContext, ModelMessagesTypeAdapter
from pydantic_ai.models.openrouter import OpenRouterModel

from services import prompts
from utils.utils import parse_incoming_history, count_tokens

load_dotenv()

# import logging
# logging.basicConfig(level=logging.DEBUG)

model_name = "deepseek/deepseek-v3.2"
# model_name = "google/gemini-3-flash-preview"
# model_name = "google/gemini-2.5-flash"
model = OpenRouterModel(
    model_name,
    provider="openrouter",
    settings=ModelSettings(extra_body={
        "reasoning": {"enabled": False},
        "provider": {"only": ["deepseek"]},
    })
)

async def get_system_prompt(ctx: RunContext[None]) -> str:
    print(ctx.deps["player"])
    prompt = prompts.get_prompt(ctx.deps["player"])
    print(prompt)
    return prompt

normal_agent = Agent[None, str](
    model,
    system_prompt=prompts.NORMAL_PROMPT
)
# normal_agent.system_prompt(dynamic=True)(get_system_prompt)

async def stream_chat_response(messages: list, player: str):
    try:
        user_message = messages[-1].get("content", "")
        history = parse_incoming_history(messages[:-1])
        agent = normal_agent

        # print(json.dumps(messages, indent=4))
        # print(ModelMessagesTypeAdapter.dump_json(history, indent=4).decode('utf-8'))

        # result = await agent.run(user_message, message_history=history)
        # yield json.dumps({"completions": {"content": result.output}})

        instructions = [
            f"The current date is {datetime.now().strftime('%Y-%m-%d')}",
            f"You are talking to the player **{player}**."
        ]

        async for event in agent.run_stream_events(user_message, message_history=history, instructions=instructions):
            if isinstance(event, PartStartEvent):
                part = event.part
                if isinstance(part, TextPart):
                    yield json.dumps({"completions": {"content": part.content}})
                # elif isinstance(part, ThinkingPart):
                #     print(event.event_kind, part.part_kind, part.content)

            elif isinstance(event, PartDeltaEvent):
                delta = event.delta
                if isinstance(delta, TextPartDelta):
                    yield json.dumps({"completions": {"content": delta.content_delta}})
                # elif isinstance(delta, ThinkingPartDelta):
                #     print(event.event_kind, delta.part_delta_kind, delta.content_delta)

            # elif isinstance(event, FunctionToolCallEvent):
            #     print(event.event_kind, event.part.__dict__)

            # elif isinstance(event, FunctionToolResultEvent):
            #     print(event.event_kind, event.__dict__)

            elif isinstance(event, AgentRunResultEvent):
                usage = event.result.usage()
                print(ModelMessagesTypeAdapter.dump_json(event.result.all_messages(), indent=4).decode('utf-8'))
                yield json.dumps({
                    "usage": {
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                        "cached_tokens": usage.cache_read_tokens,
                        "prompt_tokens": count_tokens(user_message)
                    }
                })
                # print(event.event_kind, event.result.usage().__dict__)
    except Exception as e:
        traceback.print_exc()
        yield json.dumps({"error": {"type": e.__class__.__name__, "message": str(e)}})