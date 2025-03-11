from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.auth.routers import router as auth_router
from src.openAI.routers import router as ai_router
app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ai_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/chat_ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    # Здесь можно передать данные о чатах, если они нужны в шаблоне
    return templates.TemplateResponse("chat.html", {"request": request})