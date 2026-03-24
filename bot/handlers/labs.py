from services.lms_api import lms_client


async def handle_labs(user_input: str) -> str:
    try:
        items = await lms_client.get_items()
        if not items:
            return "No labs available."

        labs = []
        for item in items:
            if item.get("type") == "lab":
                title = item.get("title", "Unknown")
                labs.append(f"Lab: {title}")

        if not labs:
            return "No labs found."

        return "Available labs:\n" + "\n".join(labs)
    except Exception as e:
        return f"Failed to fetch labs: {str(e)}"
