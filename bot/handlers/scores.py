async def handle_scores(user_input: str) -> str:
    parts = user_input.split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: /scores <lab-name> (e.g., /scores lab-04)"
    lab_name = parts[1]
    return f"Scores for {lab_name}: Not implemented yet"
