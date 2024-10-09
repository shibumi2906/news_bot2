from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger
from config import API_TOKEN
from parser import fetch_news
import sqlite3
import datetime
import asyncio

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Настройка логирования
logger.add("logs/bot.log", format="{time} {level} {message}", level="INFO")

# Настройка базы данных
conn = sqlite3.connect("news_bot.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS request_logs (
                  id INTEGER PRIMARY KEY,
                  command TEXT,
                  timestamp TEXT)''')
conn.commit()

def log_request(command: str):
    """Логирование запросов в базу данных"""
    timestamp = datetime.datetime.utcnow().isoformat()
    cursor.execute("INSERT INTO request_logs (command, timestamp) VALUES (?, ?)", (command, timestamp))
    conn.commit()

def get_last_request():
    """Получить время последнего запроса"""
    cursor.execute("SELECT timestamp FROM request_logs ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else "Нет данных"

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Я бот для парсинга новостей. Введите /help для списка команд.")
    log_request("/start")
    logger.info("Команда /start выполнена успешно")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer("Команды:\n/news - последние новости\n/last - время последнего запроса")
    log_request("/help")
    logger.info("Команда /help выполнена успешно")

@router.message(Command("news"))
async def cmd_news(message: Message):
    """Обработчик команды /news"""
    try:
        news = await fetch_news()  # Properly await the fetch_news function
        if news:
            response = "\n\n".join([f"{title}: {link}" for title, link in news])
        else:
            response = "Нет новостей."
        await message.answer(response)
        log_request("/news")
        logger.info("Команда /news выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /news: {e}")
        await message.answer("Произошла ошибка при получении новостей.")

@router.message(Command("last"))
async def cmd_last(message: Message):
    """Обработчик команды /last"""
    last_timestamp = get_last_request()
    await message.answer(f"Последний запрос был: {last_timestamp}")
    log_request("/last")
    logger.info("Команда /last выполнена успешно")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
