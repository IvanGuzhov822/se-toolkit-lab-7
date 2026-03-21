async def handle_help(user_input: str) -> str:
    return """Available commands:
/start - Welcome message
/help - Lists all available commands with descriptions
/health - Check backend status and item count
/labs - List all available labs
/scores <lab> - Get pass rates for a specific lab (e.g., /scores lab-04)"""
