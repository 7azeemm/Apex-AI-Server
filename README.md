# Apex AI Server

**The Python AI service behind Apex's in-game chat.**

This service uses FastAPI and PydanticAI to turn chat history into streamed model responses and short conversation titles. It is intended to run behind [Apex Server](https://github.com/7azeemm/Apex-Server), which handles client authentication, conversation storage, and usage limits.

## What it does

- Streams text generated through OpenRouter.
- Converts Apex message history into PydanticAI request and response objects.
- Includes a player-aware system prompt.
- Returns model token-usage information alongside generated text.
- Generates a short title for a new conversation.

The active chat model is selected in [services/models/model.py](services/models/model.py); the title model is selected separately in [services/models/chat_title_model.py](services/models/chat_title_model.py). Model names are source configuration, not a promise of provider availability.

## Local setup

Use a current Python version compatible with the dependencies in [requirements.txt](requirements.txt). The repository does not pin a Python version or lock dependency versions.

```bash
git clone https://github.com/7azeemm/Apex-AI-Server.git
cd Apex-AI-Server
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

Provide your own OpenRouter credentials in the environment or an untracked local `.env`:

```dotenv
OPENROUTER_API_KEY=replace-with-your-own-key
```

Do not commit a real key. Requests use your provider account and may incur charges.

Start the development server:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

The supplied `start.sh` uses the same host and port with a local `.venv`. Interactive API documentation is available at `http://127.0.0.1:9000/docs`.

## API

### Stream a response

`POST /chat` requires a nonempty `messages` list and a nonempty `player` string.

```bash
curl -N http://127.0.0.1:9000/chat \
  -H 'Content-Type: application/json' \
  -d '{"player":"ExamplePlayer","messages":[{"sender":"user","content":"Hello!"}]}'
```

History entries use `sender` values such as `user` and `assistant`, with a `content` string. The final message supplies the new user prompt.

The response is a **custom `text/plain` stream**: text chunks are prefixed with `content: `, followed by a JSON usage object when generation completes. Error information can also appear in the stream. This is not an OpenAI-compatible API or a standard SSE event format.

### Generate a title

`POST /generate_title` requires a nonempty `prompt` string and returns a JSON string.

```bash
curl http://127.0.0.1:9000/generate_title \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Help me understand how this project works"}'
```

The title generator currently uses the first 100 characters of the prompt and falls back to `"Chat"` if generation fails.

## Code map

| Location | Purpose |
| --- | --- |
| [main.py](main.py) | FastAPI application |
| [services/routes.py](services/routes.py) | Request validation and HTTP routes |
| [services/models/model.py](services/models/model.py) | Active chat agent and streaming logic |
| [services/models/chat_title_model.py](services/models/chat_title_model.py) | Title generation |
| [services/prompts.py](services/prompts.py) | System prompts |
| [utils/utils.py](utils/utils.py) | Message-history conversion and token helpers |
| [services/tools.py](services/tools.py) | Experimental SkyBlock tool integrations |

## Status and limitations

- The active chat path uses a general agent. The older SkyBlock tools and wiki-search code are not wired into it; some still reference an older package layout.
- Dependencies are unpinned, so fresh installs may need compatibility adjustments.
- The stream format and error handling are development interfaces and may change.
- Local prompt-token counting uses a fixed tokenizer and should not be assumed to match every provider model exactly.
- The HTTP routes do not implement authentication or per-user rate limits. Keep the service bound to localhost or a protected private network behind the backend.
- Chat content is sent to the configured model provider. Do not submit secrets or sensitive information without understanding that data flow.

## Related repositories

- [Apex](https://github.com/7azeemm/Apex) — Java/Fabric chat client.
- [Apex Server](https://github.com/7azeemm/Apex-Server) — Rust API, authentication, persistence, and usage accounting.
