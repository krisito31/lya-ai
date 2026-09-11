from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Lya AI",
    description="Asistente personal de inteligencia artificial",
    version="0.1.0"
)


class Message(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "name": "Lya",
        "status": "online",
        "message": "Hola. Soy Lya, tu asistente personal."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(data: Message):
    return {
        "assistant": "Lya",
        "response": f"Recibí tu mensaje: {data.message}"
    }
