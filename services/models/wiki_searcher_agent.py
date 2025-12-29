import json

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelSettings, RunUsage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel, ValidationError
from typing import List, Any

load_dotenv()

PROMPT = """
Your job is to get results from skyblock wiki search tool and choose which pages and sections are important based on the queries
return only chosen page titles and their chosen sections
Dont choose "Essence Crafting" section if the query does not mention "Essence"
output MUST BE IN JSON FORMAT
"""


class Page(BaseModel):
    title: str
    sections: List[str]


model_name = "openai/gpt-oss-safeguard-20b"
body = {"type": "json_object"}
model = OpenAIChatModel(
    model_name,
    provider="openrouter",
    settings=ModelSettings(extra_body=body)
)

agent = Agent[None, str](
    model,
    output_type=List[Page],
    system_prompt=PROMPT
)


async def get_relevant_pages(query: str, results: str) -> tuple[Any, RunUsage | None]:
    try:
        data = json.loads(results)
    except ValidationError as e:
        print(f"Invalid: {e}")
        return "Couldn't find information", None
    except Exception as e:
        print(f"Invalid: {e}")
        return "Couldn't find information", None

    prompt = f"Query: {query}\nPages:\n"
    for title, page in data.items():
        prompt += (
            f"- title: {title}\n"
            f"- score: {page["score"]}\n"
            f"- sections: [{', '.join(f"\"{section}\"" for section in page["sections"])}]\n\n"
        )

    print("PROMPT:")
    print(prompt)

    response = await agent.run(user_prompt=prompt)
    output = response.output
    usage = response.usage()

    print(output)
    print(usage)

    if isinstance(output, list):
        resp = []
        for page in output:
            page_info = data.get(page.title, {})
            page_data = {
                "page": page.title,
                "introduction": page_info.get("introduction", "")[:2500],
                "sections": []
            }
            for section_title in page.sections:
                content = page_info.get("sections", {}).get(section_title, "")
                page_data["sections"].append({section_title: content[:2500]})
            resp.append(page_data)
        return resp, usage
    else:
        print("Error: output is not list")
        return "Couldn't find information", None