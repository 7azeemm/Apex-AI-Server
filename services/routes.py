from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services.models.chat_title_model import generate_chat_title
from services.models.model import stream_chat_response

router = APIRouter()

@router.post("/chat")
async def chat(payload: dict):
    messages = payload.get("messages")
    if not messages or not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="Missing or invalid 'messages' field")

    player = payload.get("player")
    if not player or not isinstance(player, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'player' field")

    try:
        return StreamingResponse(stream_chat_response(messages, player), media_type="text/plain")
    except Exception as e:
        print(f"Error generating response: {e}")

        raise HTTPException(
            status_code=500,
            detail={"type": e.__class__.__name__, "message": str(e)}
        )


@router.post("/generate_title")
async def generate_title(payload: dict):
    prompt = payload.get("prompt")
    if not prompt or not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'prompt' field")

    return await generate_chat_title(prompt)