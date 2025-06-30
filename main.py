from fastapi import FastAPI, Depends, HTTPException, Security, Body
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from models import Ingredient, Recipe, AIRequest
from ai import ask_gemiai
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

app = FastAPI(title="GreenMirror AI API")


API_KEY = os.getenv("API_KEY", "123456")
api_key_header = APIKeyHeader(name="X_API_Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Yetkisiz")
    return api_key


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="GreenMirror AI API",
        version="1.0.0",
        description="Tarif ve sohbet API'si",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X_API_Key"
        }
    }
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.post("/ai/chat", tags=["AI"], summary="AI ile sohbet et", dependencies=[Depends(verify_api_key)])
async def chat_ai(request: AIRequest):
    try:
        ai_response = await ask_gemiai(request.prompt)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI hatası: {str(e)}")


@app.post("/ai/recipe_suggest", tags=["AI"], summary="AI tarif önerisi ver", dependencies=[Depends(verify_api_key)])
async def suggest_recipe(ingredients: List[str] = Body(..., embed=True)):
    try:
        ingredients_text = ", ".join(ingredients)
        prompt = (
            f"Benim elimde şu malzemeler var: {ingredients_text}.\n"
            "Bu malzemelerle yapabileceğim, düşük karbon ayak izine sahip, bitki bazlı bir yemek tarifi önerir misin?\n"
            "Tarifin adı, malzemeleri ve nasıl yapılacağını belirt lütfen."
        )
        ai_response = await ask_gemiai(prompt)
        return {"ingredients": ingredients, "recipe_suggestion": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tarif önerme hatası: {str(e)}")
