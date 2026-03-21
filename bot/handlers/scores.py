from services.lms_api import lms_client


async def handle_scores(user_input: str) -> str:
    parts = user_input.split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: /scores <lab-name> (e.g., /scores lab-04)"

    lab_name = parts[1].lower()

    try:
        pass_rates = await lms_client.get_pass_rates(lab_name)
        if not pass_rates:
            return f"No pass rate data available for {lab_name}"

        lines = [f"Pass rates for {lab_name}:"]
        for rate in pass_rates:
            task_name = rate.get("task", rate.get("task_name", "Unknown"))
            avg_score = rate.get("avg_score", rate.get("pass_rate", rate.get("average", 0)))
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

        return "\n".join(lines)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return f"Lab {lab_name} not found. Use /labs to see available labs."
        return f"Failed to fetch scores for {lab_name}: {error_msg}"
