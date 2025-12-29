import aiohttp
from aiohttp import ClientTimeout

API_URL = "http://127.0.0.1:8002/execute-tool"

async def execute_tool(tool_name: str, **args) -> str:
    payload = {
        "tool_name": tool_name,
        "args": args
    }
    print(args)

    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
            async with session.post(API_URL, json=payload) as resp:
                text = await resp.text()
                # print(text)
                if resp.status != 200:
                    return f"Tool error ({resp.status}): {text}"

                return text
    except Exception as e:
        print(e)
        return "Unexpected error while calling tool."