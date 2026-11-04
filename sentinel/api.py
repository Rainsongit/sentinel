"""FastAPI service. The role comes from the API key, never the request body,
so callers can't claim a higher role."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sentinel import domain
from sentinel.agent import Agent
from sentinel.mcp_client import MCPTools

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with MCPTools() as tools:
        state["agent"] = Agent(tools)
        yield


app = FastAPI(title="Sentinel", lifespan=lifespan)


class Chat(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.get("/health")
def health():
    return {"status": "ok", "domain": domain.current()["name"]}


@app.post("/chat")
async def chat(body: Chat, x_api_key: str = Header(...)):
    role = domain.current()["api_keys"].get(x_api_key)
    if not role:
        raise HTTPException(status_code=401, detail="invalid API key")
    return await state["agent"].handle(body.question, role)
