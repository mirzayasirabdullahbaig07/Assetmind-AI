import json
import re

from ai.groq_client import get_client
from services import report_service
import config

# Map of function name -> (callable, required_args)
SAFE_FUNCTIONS = {
    "get_assets_by_status": (report_service.get_assets_by_status, ["status"]),
    "get_assets_by_department": (report_service.get_assets_by_department, ["department_name"]),
    "get_assets_needing_attention": (report_service.get_assets_needing_attention, []),
    "get_maintenance_cost": (report_service.get_maintenance_cost, []),
    "get_repeated_repairs": (report_service.get_repeated_repairs, []),
    "get_assets_under_warranty": (report_service.get_assets_under_warranty, []),
    "get_recent_tickets": (report_service.get_recent_tickets, []),
    "get_replacements_this_year": (report_service.get_replacements_this_year, []),
    "get_assets_under_repair_count": (report_service.get_assets_under_repair_count, []),
    "get_department_with_most_issues": (report_service.get_department_with_most_issues, []),
    "get_damaged_assets_by_type": (report_service.get_damaged_assets_by_type, ["asset_type"]),
}

INTENT_SYSTEM_PROMPT = f"""You are the intent router for AssetMind's "Ask AssetMind" feature.

Given a user's question about office assets, choose EXACTLY ONE function from this list that best answers it, and extract any needed arguments from the question.

Available functions:
- get_assets_by_status(status): status is one of "Active", "Maintenance Required", "Damaged", "Under Repair", "Retired"
- get_assets_by_department(department_name): e.g. "IT Support", "HR"
- get_assets_needing_attention(): no args — assets that are Maintenance Required, Damaged, or Under Repair
- get_maintenance_cost(): no args — total repair spending
- get_repeated_repairs(): no args — assets repaired more than twice
- get_assets_under_warranty(asset_type): asset_type optional, e.g. "Laptop", pass null if not specified
- get_recent_tickets(): no args — most recent maintenance tickets
- get_replacements_this_year(): no args — assets replaced this year
- get_assets_under_repair_count(): no args — count of assets currently under repair
- get_department_with_most_issues(): no args — department with the most maintenance tickets
- get_damaged_assets_by_type(asset_type): e.g. "chair", "desktop"

Respond with ONLY a JSON object, no extra text, no markdown:
{{"function": "<function_name>", "args": {{"arg_name": "value"}}}}

If no function fits, respond with:
{{"function": "none", "args": {{}}}}
"""

ANSWER_SYSTEM_PROMPT = """You are AssetMind's assistant. You will be given the user's original question and the ACTUAL database results (as JSON).

Write a clear, concise, natural-language answer using ONLY the numbers and facts present in the JSON data. Never invent figures. Never add information not present in the data. If the data list is empty, say so plainly. Keep it to 2-4 sentences unless a short list is clearer, in which case use bullet points.
"""


def _extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return None


def _route_intent(question):
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=config.GROQ_TEXT_MODEL,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        raw = response.choices[0].message.content
        parsed = _extract_json(raw)
        return parsed
    except Exception:
        return None


def _format_answer(question, data):
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=config.GROQ_TEXT_MODEL,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}\n\nDatabase results (JSON):\n{json.dumps(data, default=str)}"},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def ask_assetmind(session, question):
    """
    Full safe pipeline: question -> Groq picks a function -> Python runs it against SQLite
    -> Groq explains the real result. Never lets the LLM invent numbers or run raw SQL.
    Returns dict: {answer, function_used, raw_data, error}
    """
    if not config.GROQ_API_KEY:
        return {
            "answer": None, "function_used": None, "raw_data": None,
            "error": "GROQ_API_KEY is not configured. Add it to your .env file to use Ask AssetMind.",
        }

    intent = _route_intent(question)
    if not intent or intent.get("function") not in SAFE_FUNCTIONS:
        return {
            "answer": "I couldn't match that question to a known data lookup. Try asking about asset status, "
                      "maintenance costs, repeated repairs, warranties, or recent tickets.",
            "function_used": None, "raw_data": None, "error": None,
        }

    func_name = intent["function"]
    args = intent.get("args") or {}
    func, required_args = SAFE_FUNCTIONS[func_name]

    call_kwargs = {}
    for arg_name in required_args:
        value = args.get(arg_name)
        if value in (None, "null", ""):
            return {
                "answer": f"I need more detail to answer that — please specify the {arg_name.replace('_', ' ')}.",
                "function_used": func_name, "raw_data": None, "error": None,
            }
        call_kwargs[arg_name] = value

    # optional args (e.g. asset_type for warranty) — pass through if present and allowed
    if func_name == "get_assets_under_warranty" and "asset_type" in args and args["asset_type"] not in (None, "null", ""):
        call_kwargs["asset_type"] = args["asset_type"]

    try:
        data = func(session, **call_kwargs)
    except Exception as e:
        return {
            "answer": None, "function_used": func_name, "raw_data": None,
            "error": f"Database query failed: {str(e)}",
        }

    answer = _format_answer(question, data)
    if answer is None:
        answer = f"Here is the data I found (AI summary unavailable): {json.dumps(data, default=str)[:500]}"

    return {"answer": answer, "function_used": func_name, "raw_data": data, "error": None}