BOT_NAME = "LMS Assistant Bot"


async def handle_start(user_input: str) -> str:
    return f"Welcome to {BOT_NAME}! Use /help to see available commands."
