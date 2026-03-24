import sys
import json
from config import settings
from services.lms_api import lms_client
from services.intent_router import (
    get_tools,
    get_system_prompt,
    format_lab_response,
    format_pass_rates,
    format_scores,
    format_groups,
    format_top_learners,
    format_timeline,
    format_completion_rate,
    format_learners,
    format_sync_result,
)


GREETINGS = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]


async def handle_natural_language(message: str) -> str:
    message_lower = message.lower().strip()

    for greeting in GREETINGS:
        if message_lower.startswith(greeting):
            return "Hello! I'm your LMS Assistant. I can help you with:\n- List available labs\n- Show pass rates and scores\n- Find top learners\n- Compare group performance\n- Check completion rates\n\nJust ask me anything about your courses!"

    tools = get_tools()
    system_prompt = get_system_prompt()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    max_iterations = 5

    for iteration in range(max_iterations):
        try:
            api_key = settings.llm_api_key
            base_url = settings.llm_api_base_url
            model = settings.llm_api_model

            async with httpx.AsyncClient(
                base_url=base_url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60.0,
            ) as client:
                response = await client.post(
                    "/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                    },
                )
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]["message"]

                if "tool_calls" in choice and choice["tool_calls"]:
                    messages.append(choice)

                    for tool_call in choice["tool_calls"]:
                        func_name = tool_call["function"]["name"]
                        func_args = tool_call["function"]["arguments"]

                        try:
                            args = json.loads(func_args) if func_args else {}
                        except json.JSONDecodeError:
                            args = {}

                        result = await execute_tool(func_name, args)
                        formatted_result = format_tool_result(func_name, result, args)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": formatted_result,
                        })
                else:
                    content = choice.get("content", "I couldn't process your request.")
                    if content:
                        return content
                    return "I don't have enough information to answer that question. Try asking about available labs, scores, or pass rates."

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "LLM authentication error (HTTP 401). Please check your LLM API key configuration."
            return f"LLM error: HTTP {e.response.status_code}"
        except httpx.ConnectError:
            return f"LLM connection error: cannot connect to {settings.llm_api_base_url}"
        except Exception as e:
            return f"LLM error: {str(e)}"

    return "I'm having trouble processing this request. Please try rephrasing your question."


async def execute_tool(name: str, args: dict):
    if name == "get_items":
        return await lms_client.get_items()
    elif name == "get_learners":
        return await lms_client.get_learners()
    elif name == "get_pass_rates":
        return await lms_client.get_pass_rates(args.get("lab", ""))
    elif name == "get_scores":
        return await lms_client.get_scores(args.get("lab", ""))
    elif name == "get_timeline":
        return await lms_client.get_timeline(args.get("lab", ""))
    elif name == "get_groups":
        return await lms_client.get_groups(args.get("lab", ""))
    elif name == "get_top_learners":
        return await lms_client.get_top_learners(args.get("lab", ""), args.get("limit", 5))
    elif name == "get_completion_rate":
        return await lms_client.get_completion_rate(args.get("lab", ""))
    elif name == "trigger_sync":
        return await lms_client.trigger_sync()

    return {"error": f"Unknown tool: {name}"}


def format_tool_result(name: str, result, args: dict) -> str:
    if isinstance(result, dict) and "error" in result:
        return json.dumps(result)

    if name == "get_items":
        return format_lab_response(result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_pass_rates":
        lab = args.get("lab", "unknown")
        return format_pass_rates(lab, result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_scores":
        lab = args.get("lab", "unknown")
        return format_scores(lab, result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_groups":
        lab = args.get("lab", "unknown")
        return format_groups(lab, result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_top_learners":
        lab = args.get("lab", "unknown")
        return format_top_learners(lab, result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_timeline":
        lab = args.get("lab", "unknown")
        return format_timeline(lab, result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "get_completion_rate":
        lab = args.get("lab", "unknown")
        return format_completion_rate(lab, result) if isinstance(result, dict) else json.dumps(result, default=str)
    elif name == "get_learners":
        return format_learners(result) if isinstance(result, list) else json.dumps(result, default=str)
    elif name == "trigger_sync":
        return format_sync_result(result) if isinstance(result, dict) else json.dumps(result, default=str)

    return json.dumps(result, default=str)


import httpx
