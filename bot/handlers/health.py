from services.lms_api import lms_client


async def handle_health(user_input: str) -> str:
    is_healthy, message = await lms_client.health_check()
    return message
