"""
Supabase helper functions for auth_router.py.
Replaces direct sqlite3.connect calls.
"""
import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://girgnqnswoelalccvqkh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _get(table, select="*", filters=None):
    """GET from Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}"
    if filters:
        for k, v in filters.items():
            url += f"&{k}=eq.{v}"
    resp = requests.get(url, headers=_HEADERS)
    resp.raise_for_status()
    return resp.json()


def _insert(table, data):
    """INSERT via Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.post(url, headers=_HEADERS, json=data)
    if resp.status_code == 409:
        return None  # Conflict (already exists)
    resp.raise_for_status()
    result = resp.json()
    return result[0] if result else data


def _update(table, id_field, id_val, data):
    """UPDATE via Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{id_field}=eq.{id_val}"
    resp = requests.patch(url, headers=_HEADERS, json=data)
    resp.raise_for_status()
    result = resp.json()
    return result[0] if result else data


def _query(sql_text, params=None):
    """
    Fallback for complex queries not easily mappable to REST.
    Uses Supabase Management API (requires service_role key).
    """
    # For simple auth queries, map them manually to REST calls
    # This is a compatibility layer — prefer _get/_insert/_update when possible
    raise NotImplementedError("Use _get/_insert/_update instead of raw SQL")


def find_student_by_display(display_name):
    """Find student by display name (case-insensitive lookup on Supabase)."""
    rows = _get("students", select="id,class_id,project_id")
    # Client-side case-insensitive match (Supabase REST API doesn't support ILIKE)
    name_lower = display_name.lower()
    for r in rows:
        if r.get("id", "").lower() == name_lower or r.get("display", "").lower() == name_lower:
            return (r["id"], r["class_id"], r.get("project_id"))
    return None


def find_user_by_name(name):
    """Find user by name."""
    rows = _get("users", select="id,name,role,token")
    for r in rows:
        if r.get("name", "").lower() == name.lower():
            return (r["id"], r["name"], r["role"], r["token"])
    return None


def create_user(user_id, name, role, token):
    """Create a new user."""
    return _insert("users", {"id": user_id, "name": name, "role": role, "token": token})


def find_user_by_token(token):
    """Find user by auth token."""
    rows = _get("users", select="id,name,role", filters={"token": token})
    if rows:
        r = rows[0]
        return (r["id"], r["name"], r["role"])
    return None


def list_classes():
    """List all classes."""
    return _get("classes", select="id,name,subject,created_at")


def list_students_by_class(class_id):
    """List students in a class."""
    return _get("students", select="id,class_id,display,project_id,milestone,progress", filters={"class_id": class_id})


def update_student(id_val, class_id_val, data):
    """Update student fields."""
    url = f"{SUPABASE_URL}/rest/v1/students?id=eq.{id_val}&class_id=eq.{class_id_val}"
    resp = requests.patch(url, headers=_HEADERS, json=data)
    resp.raise_for_status()
    result = resp.json()
    return result[0] if result else data


def delete_class(class_id):
    """Delete a class and its students (cascade)."""
    # Delete students first
    requests.delete(f"{SUPABASE_URL}/rest/v1/students?class_id=eq.{class_id}", headers=_HEADERS)
    # Then delete class
    resp = requests.delete(f"{SUPABASE_URL}/rest/v1/classes?id=eq.{class_id}", headers=_HEADERS)
    resp.raise_for_status()


def create_class(class_id, name, subject=""):
    """Create a new class."""
    return _insert("classes", {"id": class_id, "name": name, "subject": subject})


def find_user_by_id(user_id):
    """Find user by ID."""
    rows = _get("users", select="id,name,role,token", filters={"id": user_id})
    if rows:
        r = rows[0]
        return (r["id"], r["name"], r["role"], r["token"])
    return None


def get_user_key(user_id, provider):
    """Get user API key status (not the actual key)."""
    # Since user_keys is not a standard Supabase table with REST endpoint,
    # we'll need to query it via the SQL endpoint or add it to migrations
    # For now, return not_set
    return None


def set_user_key(user_id, provider, api_key):
    """Save user API key."""
    try:
        return _insert("user_keys", {
            "user_id": user_id,
            "provider": provider,
            "api_key": api_key
        })
    except Exception:
        return None


def find_student_by_id_and_class(student_id, class_id):
    """Find student by ID and class."""
    rows = _get("students", select="id,display,project_id,class_id", filters={"id": student_id, "class_id": class_id})
    if rows:
        r = rows[0]
        return (r["id"], r["display"], r.get("project_id"), r["class_id"])
    return None


def update_user_password(user_id, password_hash):
    """Update user password hash."""
    return _update("users", "id", user_id, {"password_hash": password_hash})


def find_user_by_name_with_password(name):
    """Find user by name including password hash."""
    rows = _get("users", select="id,name,role,token,password_hash")
    for r in rows:
        if r.get("name", "").lower() == name.lower():
            return (r["id"], r["name"], r["role"], r["token"], r.get("password_hash"))
    return None
