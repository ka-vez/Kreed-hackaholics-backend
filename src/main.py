from fastapi import FastAPI
from .api.v1 import chat

app = FastAPI(title="BelAI")

app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"Hello": "BelAI"}
