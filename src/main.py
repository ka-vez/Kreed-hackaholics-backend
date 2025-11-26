# internal imports
from src.api.v1 import chat
from src.database.database import create_db_and_tables

#external imports
from fastapi import FastAPI


app = FastAPI(title="BelAI")

create_db_and_tables()

app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"Hello": "BelAI"}
