from fastapi import FastAPI

from services.routes import router

app = FastAPI(title="LLM Server")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001)

# The server runs with:
# uvicorn main:app --host 127.0.0.1 --port 8001