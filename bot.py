"""
Telegram AI-ассистент для ответов на вопросы о компании.
Использует Claude API как мозг и файл company_info.txt как базу знаний.
"""

import asyncio
import logging
import os
from anthropic import Anthropic
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message

# ─── Настройка логирования ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Конфигурация (из переменных окружения) ──────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# ─── Клиенты ─────────────────────────────────────────────────────────────────
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ─── Загрузка информации о компании ──────────────────────────────────────────
def load_company_info(path: str = "company_info.txt") -> str:
    """Загружает текстовый файл с информацией о компании."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        logger.info(f"Загружена информация о компании: {len(content)} символов")
        return content
    except FileNotFoundError:
        logger.warning(f"Файл {path} не найден. Бот будет работать без базы знаний.")
        return "Информация о компании не загружена."

COMPANY_INFO = load_company_info()

# ─── Системный промпт для AI ──────────────────────────────────────────────────
SYSTEM_PROMPT = f"""Ты — умный и дружелюбный AI-ассистент компании. 
Твоя задача — отвечать на вопросы пользователей о компании, её услугах, продуктах, команде и вакансиях.

Используй только информацию из базы знаний ниже. 
Если вопрос выходит за рамки этой информации — честно скажи об этом и предложи связаться с менеджером.

Отвечай кратко, по делу, на том языке, на котором пишет пользователь (русский или казахский). Не используй никакого форматирования — никаких звёздочек, решёток, тире в начале строк. Только обычный текст.

═══════════════════════════════
БАЗА ЗНАНИЙ О КОМПАНИИ:
═══════════════════════════════
{COMPANY_INFO}
═══════════════════════════════
"""

# ─── История диалогов (в памяти, per user) ───────────────────────────────────
# Формат: {{ user_id: [{"role": "user"/"assistant", "content": "..."}] }}
conversation_history: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # максимум сообщений в истории одного пользователя


def get_history(user_id: int) -> list[dict]:
    return conversation_history.setdefault(user_id, [])


def add_to_history(user_id: int, role: str, content: str):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    # Обрезаем историю если слишком длинная
    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]


# ─── Запрос к Claude ─────────────────────────────────────────────────────────
def ask_claude(user_id: int, user_message: str) -> str:
    """Отправляет сообщение в Claude с историей диалога и возвращает ответ."""
    add_to_history(user_id, "user", user_message)
    
    try:
        response = anthropic.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=get_history(user_id),
        )
        answer = response.content[0].text
        add_to_history(user_id, "assistant", answer)
        return answer
    except Exception as e:
        logger.error(f"Ошибка Claude API: {e}")
        # Убираем последнее сообщение пользователя из истории при ошибке
        get_history(user_id).pop()
        return "Произошла ошибка. Попробуйте задать вопрос ещё раз."


# ─── Хэндлеры Telegram ───────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Приветствие при /start."""
    user_name = message.from_user.first_name or "друг"
    await message.answer(
     f"Привет, {user_name}! 👋\n\n"
"Я AI-ассистент магазина Центр Красок #1. "
"Отвечу на любые вопросы о красках, брендах, колеровке, доставке и ценах.\n\n"
"Просто напишите свой вопрос!"
    )


@dp.message()
async def handle_message(message: Message):
    """Обрабатывает все входящие сообщения."""
    user_id = message.from_user.id
    user_text = message.text or ""

    if not user_text.strip():
        return

    # Показываем «печатает...»
    await bot.send_chat_action(message.chat.id, "typing")

    logger.info(f"[User {user_id}] {user_text[:80]}")

    # Получаем ответ от Claude (синхронный вызов в executor)
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, ask_claude, user_id, user_text)

    await message.answer(answer)
    logger.info(f"[Bot → {user_id}] {answer[:80]}")


# ─── Запуск ───────────────────────────────────────────────────────────────────
async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
