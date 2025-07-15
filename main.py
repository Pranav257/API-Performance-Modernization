from fastapi import FastAPI, Request
from app.routes import user_router, genai_router
import logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(user_router, prefix="/user")
app.include_router(genai_router, prefix="/genai")

FastAPIInstrumentor().instrument_app(app)

@app.get("/")
def health():
    return {"status": "user service running"}
