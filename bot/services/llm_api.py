import httpx
from config import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url
        self.model = settings.llm_api_model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=120.0,
            )
        return self._client

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_iterations: int = 10,
    ) -> str:
        client = await self._get_client()

        for _ in range(max_iterations):
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.model,
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
                    import json

                    try:
                        args = json.loads(func_args) if func_args else {}
                    except json.JSONDecodeError:
                        args = {}

                    result = await self._execute_tool(func_name, args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    })
            else:
                return choice.get("content", "I couldn't process your request.")

        return "I'm having trouble processing this request. Please try again."

    async def _execute_tool(self, name: str, args: dict) -> str:
        from services.lms_api import lms_client
        import json

        tool_methods = {
            "get_items": lms_client.get_items,
            "get_learners": lms_client.get_learners,
            "get_scores": lms_client.get_scores,
            "get_pass_rates": lms_client.get_pass_rates,
            "get_timeline": lms_client.get_timeline,
            "get_groups": lms_client.get_groups,
            "get_top_learners": lms_client.get_top_learners,
            "get_completion_rate": lms_client.get_completion_rate,
            "trigger_sync": lms_client.trigger_sync,
        }

        method = tool_methods.get(name)
        if not method:
            return f"Unknown tool: {name}"

        try:
            if name == "get_pass_rates":
                result = await method(args.get("lab", ""))
            elif name == "get_scores":
                result = await method(args.get("lab", ""))
            elif name == "get_timeline":
                result = await method(args.get("lab", ""))
            elif name == "get_groups":
                result = await method(args.get("lab", ""))
            elif name == "get_top_learners":
                result = await method(args.get("lab", ""), args.get("limit", 5))
            elif name == "get_completion_rate":
                result = await method(args.get("lab", ""))
            elif name == "trigger_sync":
                result = await method()
            else:
                result = await method()

            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"


llm_client = LLMClient()
