import argparse
import asyncio
import sys

from handlers import help, health, labs, scores, start, natural_language
from services.lms_api import lms_client
from services.intent_router import get_tools


COMMANDS = {
    "/start": start.handle_start,
    "/help": help.handle_help,
    "/health": health.handle_health,
    "/labs": labs.handle_labs,
    "/scores": scores.handle_scores,
}

KEYBOARD_BUTTONS = [
    [{"text": "📚 Available Labs", "callback_data": "labs"}, {"text": "📊 My Scores", "callback_data": "scores"}],
    [{"text": "❤️ Health Check", "callback_data": "health"}, {"text": "❓ Help", "callback_data": "help"}],
    [{"text": "🏆 Top Learners", "callback_data": "top_learners"}, {"text": "📈 Timeline", "callback_data": "timeline"}],
]


async def process_command(command: str) -> str:
    parts = command.strip().split()
    cmd = parts[0].lower() if parts else ""

    handler = COMMANDS.get(cmd)
    if handler:
        return await handler(command)

    return await natural_language.handle_natural_language(command)


async def process_natural_query(query: str) -> str:
    return await natural_language.handle_natural_language(query)


async def run_test_mode(command: str) -> None:
    response = await process_command(command)
    print(response)


async def run_telegram_mode() -> None:
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import CommandStart, Command
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from config import settings

    if not settings.bot_token:
        print("Error: BOT_TOKEN not set. Please check .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    def get_main_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📚 Available Labs", callback_data="labs")],
                [InlineKeyboardButton(text="📊 My Scores", callback_data="scores")],
                [InlineKeyboardButton(text="❤️ Health Check", callback_data="health")],
                [InlineKeyboardButton(text="❓ Help", callback_data="help")],
            ]
        )

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        response = await start.handle_start("/start")
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = await help.handle_help("/help")
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        response = await health.handle_health("/health")
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = await labs.handle_labs("/labs")
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        args = message.text.split(maxsplit=1)
        command_with_args = f"/scores {args[1]}" if len(args) > 1 else "/scores"
        response = await scores.handle_scores(command_with_args)
        await message.answer(response)

    @dp.callback_query(F.data == "labs")
    async def callback_labs(callback: types.CallbackQuery):
        response = await labs.handle_labs("/labs")
        await callback.message.answer(response)
        await callback.answer()

    @dp.callback_query(F.data == "scores")
    async def callback_scores(callback: types.CallbackQuery):
        await callback.message.answer("Send me the lab name, e.g., 'lab-04'")
        await callback.answer()

    @dp.callback_query(F.data == "health")
    async def callback_health(callback: types.CallbackQuery):
        response = await health.handle_health("/health")
        await callback.message.answer(response)
        await callback.answer()

    @dp.callback_query(F.data == "help")
    async def callback_help(callback: types.CallbackQuery):
        response = await help.handle_help("/help")
        await callback.message.answer(response)
        await callback.answer()

    @dp.message()
    async def handle_text_message(message: types.Message):
        if message.text:
            response = await natural_language.handle_natural_language(message.text)
            await message.answer(response)

    await dp.start_polling(bot)


def main() -> None:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the specified command (e.g., --test '/start')",
    )

    args = parser.parse_args()

    if args.test:
        asyncio.run(run_test_mode(args.test))
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
