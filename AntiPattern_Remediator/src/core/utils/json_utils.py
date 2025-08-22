import json

def extract_first_json(text):
    """
    Try to extract the first JSON object from a string.
    Works if JSON is inside ```json ... ``` fences or just plain text.
    """
    if not isinstance(text, str):
        return None

    # 1. If the text has fenced JSON like ```json ... ```
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            # Look for JSON-specific fences
            if part.strip().lower().startswith("json"):
                json_part = part[len("json"):].strip()
                try:
                    return json.loads(json_part)
                except Exception:
                    pass  # Try next part

    # 2. If no fenced JSON worked, try to parse the whole text
    try:
        return json.loads(text.strip())
    except Exception:
        return None