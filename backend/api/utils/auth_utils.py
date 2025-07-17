from fastapi import Request, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()
API_SECRET = os.getenv("API_SECRET")
WEB_API_SECRET = os.getenv("WEB_API_SECRET")

async def verificar_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o formato incorrecto")
    
    token_value = token.split(" ")[1]
    if token_value != API_SECRET:
        raise HTTPException(status_code=401, detail="Token inválido")
    
async def verificar_token_web(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Acceso denegado: Token inválido o ausente")

    token_value = token.split(" ")[1]
    if token_value != WEB_API_SECRET:
        raise HTTPException(status_code=403, detail="Acceso denegado: Token no autorizado")