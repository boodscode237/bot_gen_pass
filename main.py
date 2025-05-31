import os
import sys
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from dotenv import load_dotenv

from app.config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET, ADMIN_USER_ID
from app.handlers import router

load_dotenv()

app = FastAPI()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"


@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL is None or WEBHOOK_SECRET is None:
        print(
            "Please set WEBHOOK_URL and WEBHOOK_SECRET in environment!", file=sys.stderr
        )
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


# Secure API for ADMIN_USER_ID only (optionnel)
@app.get("/download_passwords")
async def download_passwords(user_id: int):
    if user_id != ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="Forbidden")
    if os.path.exists("passwords.json"):
        with open("passwords.json", "rb") as f:
            return f.read()
    else:
        return b"No passwords yet."
