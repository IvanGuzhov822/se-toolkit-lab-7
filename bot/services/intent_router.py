import json

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all available labs and tasks",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 5"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System (LMS). You have access to backend data through tools.

When a user asks about labs, scores, students, or any learning data, use the available tools to fetch real data and provide accurate answers.

Always use tools to get actual data before answering. Do not make up numbers or lab names.

If the user asks a greeting or simple question, respond naturally without using tools.

If you don't understand the query, ask for clarification or suggest what you can help with.

Available capabilities:
- List available labs and tasks
- Show pass rates and scores for specific labs
- Show top learners and group performance
- Show completion rates and timelines
- Trigger data sync"""


def get_tools() -> list[dict]:
    return TOOLS


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def format_lab_response(items: list[dict]) -> str:
    if not items:
        return "No labs available."

    labs = []
    for item in items:
        if item.get("type") == "lab":
            title = item.get("title", "Unknown")
            labs.append(f"- {title}")

    if not labs:
        return "No labs found."

    return "Available labs:\n" + "\n".join(labs)


def format_pass_rates(lab: str, rates: list[dict]) -> str:
    if not rates:
        return f"No pass rate data available for {lab}."

    lines = [f"Pass rates for {lab}:"]
    for rate in rates:
        task_name = rate.get("task", rate.get("task_name", "Unknown"))
        avg_score = rate.get("avg_score", rate.get("pass_rate", rate.get("average", 0)))
        attempts = rate.get("attempts", 0)
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

    return "\n".join(lines)


def format_scores(lab: str, scores: list[dict]) -> str:
    if not scores:
        return f"No score data available for {lab}."

    lines = [f"Score distribution for {lab}:"]
    for bucket in scores:
        label = bucket.get("label", bucket.get("bucket", "Unknown"))
        count = bucket.get("count", 0)
        lines.append(f"- {label}: {count} students")

    return "\n".join(lines)


def format_groups(lab: str, groups: list[dict]) -> str:
    if not groups:
        return f"No group data available for {lab}."

    lines = [f"Group performance for {lab}:"]
    for group in groups:
        name = group.get("group_name", group.get("group", "Unknown"))
        avg = group.get("avg_score", group.get("average", 0))
        count = group.get("student_count", group.get("count", 0))
        lines.append(f"- {name}: {avg:.1f}% avg ({count} students)")

    return "\n".join(lines)


def format_top_learners(lab: str, learners: list[dict]) -> str:
    if not learners:
        return f"No top learners data available for {lab}."

    lines = [f"Top learners for {lab}:"]
    for i, learner in enumerate(learners, 1):
        name = learner.get("name", learner.get("learner_name", "Unknown"))
        score = learner.get("avg_score", learner.get("score", 0))
        lines.append(f"{i}. {name}: {score:.1f}%")

    return "\n".join(lines)


def format_timeline(lab: str, timeline: list[dict]) -> str:
    if not timeline:
        return f"No timeline data available for {lab}."

    lines = [f"Submission timeline for {lab}:"]
    for entry in timeline[:10]:
        date = entry.get("date", entry.get("day", "Unknown"))
        count = entry.get("count", entry.get("submissions", 0))
        lines.append(f"- {date}: {count} submissions")

    return "\n".join(lines)


def format_completion_rate(lab: str, data: dict) -> str:
    if not data:
        return f"No completion rate data available for {lab}."

    rate = data.get("completion_rate", data.get("rate", 0))
    total = data.get("total_students", data.get("total", 0))
    completed = data.get("completed", 0)
    return f"Completion rate for {lab}: {rate:.1f}% ({completed}/{total} students)"


def format_learners(learners: list[dict]) -> str:
    if not learners:
        return "No learners data available."

    count = len(learners)
    return f"Total enrolled students: {count}"


def format_sync_result(result: dict) -> str:
    return f"Sync triggered successfully. Status: {result.get('status', 'pending')}"
