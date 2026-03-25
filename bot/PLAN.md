Telegram Bot Development Plan for LMS

This document describes the approach to implementing all bot tasks including basic architecture, backend integration, intent routing, and deployment.

The bot architecture is built around the principle of handler testability. The core idea is that command processing logic is separated from the Telegram transport layer. Each handler is a function that takes a user input string and returns a response string. This allows running handlers directly in test mode without connecting to the Telegram API, which simplifies development and testing.

The bot implements slash commands (/start, /help, /health, /labs, /scores) that work with real backend data. Each command fetches live data from the LMS API and formats it for the user. Error handling provides friendly messages when the backend is unavailable.

For natural language queries, the bot uses an LLM-powered intent router. The LLM receives tool definitions for all 9 backend endpoints (get_items, get_learners, get_scores, get_pass_rates, get_timeline, get_groups, get_top_learners, get_completion_rate, trigger_sync) and decides which tools to call based on the user's message. The bot executes the tool calls, feeds results back to the LLM, and the LLM produces a natural language summary. This enables multi-step reasoning where the LLM can call multiple tools sequentially to answer complex questions like "which lab has the lowest pass rate".

Inline keyboard buttons are provided for quick access to common actions. After /start, users see buttons for Available Labs, My Scores, Health Check, and Help. This improves discoverability and reduces the need for typing.

Backend integration uses the services/lms_api.py module which wraps all HTTP calls to the LMS API. The LLM client in services/llm_api.py handles the tool calling loop with the Qwen Code API. Tool schemas are defined in services/intent_router.py along with response formatters.

Bot deployment is performed on a virtual machine using Docker Compose for consistency with the rest of the project infrastructure. The bot runs as a background process with logging to bot.log for debugging. Automatic restart on failure is configured.

Testing includes both automated tests in --test mode and manual verification through Telegram. Natural language queries like "what labs are available", "show me scores for lab 4", and "which lab has the lowest pass rate" are verified to return real backend data. Edge cases like gibberish input and greetings are handled gracefully. Before each merge, all tests must pass and the bot must be verified to work in a real chat.
