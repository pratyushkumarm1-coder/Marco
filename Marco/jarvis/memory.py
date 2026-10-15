from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_KEY, CONTEXT_LIMIT


client = None


def get_client():
    global client
    if client is None:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return client


def save_message(role: str, message: str, command_type: str = None):
    db = get_client()
    data = {"role": role, "message": message}
    if command_type:
        data["command_type"] = command_type
    db.table("conversations").insert(data).execute()


def get_history(limit: int = CONTEXT_LIMIT) -> list[dict]:
    db = get_client()
    response = (
        db.table("conversations")
        .select("role, message")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    messages = response.data
    messages.reverse()
    return [{"role": m["role"], "content": m["message"]} for m in messages]


def log_command(command: str, parameters: dict = None, status: str = "success", response: str = ""):
    db = get_client()
    db.table("command_logs").insert({
        "command": command,
        "parameters": parameters or {},
        "status": status,
        "response": response,
    }).execute()


def clear_history():
    db = get_client()
    db.table("conversations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
