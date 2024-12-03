from fastapi import FastAPI
from pilot import Pilot

app = FastAPI(
    title="AI_Devs 3 - Mission 19 - API",
    version="1.0.0",
    openapi_url=None,
)
pilot = Pilot()

@app.get("/", summary="Home page")
def home():
    return {"message": "Hello Agent 5!"}

@app.post("/webhook")
async def webhook(input: dict) -> dict:
    return await pilot.description(input["instruction"])
