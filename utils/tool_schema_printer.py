import json

from pydantic_ai import ModelMessage, TextPart, ModelResponse
from pydantic_ai.models.function import AgentInfo, FunctionModel

from llm_service.models.model import skyblock_agent

def print_tools_schema(_: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    for tool in info.function_tools:
        print(json.dumps(tool.__dict__, indent=4))
    return ModelResponse(parts=[TextPart("hello world")])

skyblock_agent.run_sync('', model=FunctionModel(print_tools_schema))