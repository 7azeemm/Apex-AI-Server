from typing import List, Dict, Any

import tiktoken
from pydantic_ai import ModelRequest, ModelResponse
from pydantic_ai.messages import UserPromptPart, TextPart, ToolCallPart, ToolReturnPart

tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(prompt: str) -> int:
    return len(tokenizer.encode(prompt))


def extract_tool_data(messages: List[ModelRequest | ModelResponse]) -> List[Dict[str, Any]]:
    """
    Scans the message history for complete tool executions.
    Pairs ToolCallPart (args) with ToolReturnPart (content) using the tool_call_id.
    """
    calls_map = {}
    complete_tools = []

    # 1. First pass: Collect all Tool Calls (Requests to run tools)
    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    calls_map[part.tool_call_id] = {
                        "tool_name": part.tool_name,
                        "args": part.args
                    }

    # 2. Second pass: Collect Tool Returns and match them with Calls
    for msg in messages:
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    call_id = part.tool_call_id

                    # Only proceed if we have the matching call info
                    if call_id in calls_map:
                        call_info = calls_map[call_id]

                        complete_tools.append({
                            "tool_call_id": call_id,
                            "tool_name": call_info["tool_name"],
                            "args": call_info["args"],
                            "content": part.content
                        })

    return complete_tools


def parse_incoming_history(rust_messages: list) -> List[ModelRequest | ModelResponse]:
    pydantic_history = []

    for msg in rust_messages:
        role = msg.get("sender")
        content = msg.get("content", "")

        if role == "user":
            pydantic_history.append(ModelRequest(parts=[UserPromptPart(content=content)]))

        elif role == "assistant":
            tools = msg.get("tools", [])
            if tools:
                # 1. Reconstruct the Tool Calls (What the AI asked for)
                call_parts = []
                return_parts = []

                for t in tools:
                    # Part A: The Call
                    call_parts.append(ToolCallPart(
                        tool_name=t['tool_name'],
                        args=t['args'],
                        tool_call_id=t['tool_call_id']
                    ))

                    # Part B: The Result
                    return_parts.append(ToolReturnPart(
                        tool_name=t['tool_name'],
                        content=t['content'],
                        tool_call_id=t['tool_call_id']
                    ))

                # Step 1: Add the Assistant's Request to run tools
                pydantic_history.append(ModelResponse(parts=call_parts))

                # Step 2: Add the Tool's Result (ModelRequest simulating the system return)
                pydantic_history.append(ModelRequest(parts=return_parts))

            # Step 3: Finally, add the actual Text the AI spoke
            if content:
                pydantic_history.append(ModelResponse(parts=[TextPart(content=content)]))

    return pydantic_history