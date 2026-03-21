async def handle_help(user_input: str) -> str:
    return """Available commands:
/start - Start the bot
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""
