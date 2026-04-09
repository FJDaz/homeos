"""
Supabase Client — REST API wrapper for AetherFlow.
Replaces SQLite-based bkd_service for class/student/project data.

Provides a `supabase_db_con()` context manager that mimics SQLite cursor
so existing class_router.py code works with minimal changes.
"""
import os
import requests
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from functools import lru_cache

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://girgnqnswoelalccvqkh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class SupabaseCursor:
    """
    Mimics sqlite3 cursor for class_router compatibility.
    Only supports the queries actually used in class_router.py.
    """
    def __init__(self):
        self.url = SUPABASE_URL
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self._rows = []
        self._rowcount = 0

    def execute(self, sql: str, params: tuple = None):
        """Parse SQL and dispatch to Supabase REST API."""
        sql_lower = sql.lower().strip()

        if sql_lower.startswith("select"):
            self._handle_select(sql_lower, params)
        elif sql_lower.startswith("insert"):
            self._handle_insert(sql_lower, params)
        elif sql_lower.startswith("update"):
            self._handle_update(sql_lower, params)
        elif sql_lower.startswith("delete"):
            self._handle_delete(sql_lower, params)
        return self

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def _handle_select(self, sql_lower: str, params: tuple = None):
        """Parse SELECT and dispatch to Supabase."""
        if "from classes" in sql_lower:
            self._rows = self._select_classes(sql_lower, params)
        elif "from students" in sql_lower:
            self._rows = self._select_students(sql_lower, params)
        elif "from projects" in sql_lower:
            self._rows = self._select_projects(sql_lower, params)
        else:
            raise NotImplementedError(f"Unsupported SELECT from: {sql_lower[:100]}")

    def _select_classes(self, sql: str, params: tuple = None):
        """Handle classes SELECT queries."""
        if "from classes order by" in sql:
            # SELECT id, name, subject, created_at FROM classes ORDER BY ...
            resp = requests.get(f"{self.url}/rest/v1/classes?select=id,name,subject,created_at&order=created_at.desc", headers=self.headers)
        elif "where id=?" in sql and params:
            resp = requests.get(f"{self.url}/rest/v1/classes?id=eq.{params[0]}", headers=self.headers)
        else:
            resp = requests.get(f"{self.url}/rest/v1/classes?select=*", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def _select_students(self, sql: str, params: tuple = None):
        """Handle students SELECT queries."""
        if "where class_id=?" in sql and params:
            resp = requests.get(f"{self.url}/rest/v1/students?select=id,display,nom,prenom,project_id,milestone,class_id&class_id=eq.{params[0]}", headers=self.headers)
        elif "where id=?" in sql and params:
            resp = requests.get(f"{self.url}/rest/v1/students?select=*&id=eq.{params[0]}", headers=self.headers)
        elif "where id=? and class_id=?" in sql and params:
            resp = requests.get(f"{self.url}/rest/v1/students?select=*&id=eq.{params[0]}&class_id=eq.{params[1]}", headers=self.headers)
        else:
            resp = requests.get(f"{self.url}/rest/v1/students?select=*", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def _select_projects(self, sql: str, params: tuple = None):
        """Handle projects SELECT queries."""
        if "where id=?" in sql and params:
            resp = requests.get(f"{self.url}/rest/v1/projects?id=eq.{params[0]}", headers=self.headers)
        else:
            resp = requests.get(f"{self.url}/rest/v1/projects?select=*", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def _handle_insert(self, sql: str, params: tuple = None):
        """Handle INSERT statements."""
        if "into classes" in sql.lower():
            # INSERT INTO classes (id, name, subject, created_at) VALUES (?, ?, ?, ?)
            data = {"id": params[0], "name": params[1], "subject": params[2]} if params else {}
            resp = requests.post(f"{self.url}/rest/v1/classes", headers=self.headers, json=data)
            if resp.status_code == 409:  # Conflict = already exists
                self._rowcount = 0
                return
            resp.raise_for_status()
            self._rowcount = 1
        elif "into students" in sql.lower():
            data = {
                "id": params[0], "class_id": params[1], "display": params[2],
                "last_name": params[3], "first_name": params[4],
                "project_id": params[5] if len(params) > 5 and params[5] else None,
                "milestone": params[6] if len(params) > 6 else 0,
            }
            resp = requests.post(f"{self.url}/rest/v1/students", headers=self.headers, json=data)
            if resp.status_code == 409:
                self._rowcount = 0
                return
            resp.raise_for_status()
            self._rowcount = 1
        else:
            raise NotImplementedError(f"Unsupported INSERT: {sql[:100]}")

    def _handle_update(self, sql: str, params: tuple = None):
        """Handle UPDATE statements."""
        if "update students" in sql.lower():
            if "where class_id=?" in sql.lower() and params:
                # Bulk update milestone by class_id
                url = f"{self.url}/rest/v1/students?class_id=eq.{params[1]}"
            elif "where id=?" in sql.lower() and params:
                url = f"{self.url}/rest/v1/students?id=eq.{params[1]}"
            else:
                raise NotImplementedError(f"Unsupported UPDATE students: {sql[:100]}")
            data = {"milestone": params[0]}
            resp = requests.patch(url, headers=self.headers, json=data)
            resp.raise_for_status()
            self._rowcount = 1
        elif "update classes" in sql.lower() and params:
            # UPDATE classes SET name=?, subject=? WHERE id=?
            url = f"{self.url}/rest/v1/classes?id=eq.{params[2]}"
            data = {"name": params[0], "subject": params[1]}
            resp = requests.patch(url, headers=self.headers, json=data)
            resp.raise_for_status()
            self._rowcount = 1
        else:
            raise NotImplementedError(f"Unsupported UPDATE: {sql[:100]}")

    def _handle_delete(self, sql: str, params: tuple = None):
        """Handle DELETE statements."""
        if "from students" in sql.lower() and params:
            url = f"{self.url}/rest/v1/students?class_id=eq.{params[0]}"
        elif "from classes" in sql.lower() and params:
            url = f"{self.url}/rest/v1/classes?id=eq.{params[0]}"
        else:
            raise NotImplementedError(f"Unsupported DELETE: {sql[:100]}")
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
        self._rowcount = 1


@contextmanager
def supabase_db_con():
    """Context manager mimicking bkd_db_con() for class_router compatibility."""
    con = SupabaseCursor()
    try:
        yield con
    finally:
        pass


class SupabaseClient:
    def __init__(self):
        self.url = SUPABASE_URL
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _get(self, table: str, params: str = "*", filters: dict = None) -> List[Dict]:
        url = f"{self.url}/rest/v1/{table}?select={params}"
        if filters:
            for key, val in filters.items():
                url += f"&{key}=eq.{val}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def _insert(self, table: str, data: Dict) -> Dict:
        url = f"{self.url}/rest/v1/{table}"
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        return result[0] if result else data

    def _update(self, table: str, id_field: str, id_val: str, data: Dict) -> Dict:
        url = f"{self.url}/rest/v1/{table}?{id_field}=eq.{id_val}"
        resp = requests.patch(url, headers=self.headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        return result[0] if result else data

    def _delete(self, table: str, id_field: str, id_val: str):
        url = f"{self.url}/rest/v1/{table}?{id_field}=eq.{id_val}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()

    # --- Classes ---
    def list_classes(self) -> List[Dict]:
        return self._get("classes", "id,name,subject,created_at")

    def get_class(self, class_id: str) -> Optional[Dict]:
        rows = self._get("classes", "id,name,subject,created_at", {"id": class_id})
        return rows[0] if rows else None

    def create_class(self, class_id: str, name: str, subject: str = "") -> Dict:
        return self._insert("classes", {"id": class_id, "name": name, "subject": subject})

    def update_class(self, class_id: str, data: Dict) -> Dict:
        return self._update("classes", "id", class_id, data)

    def delete_class(self, class_id: str):
        self._delete("classes", "id", class_id)

    # --- Students ---
    def list_students(self, class_id: str = None) -> List[Dict]:
        filters = {"class_id": class_id} if class_id else None
        return self._get("students", "id,class_id,display,last_name,first_name,project_id,progress", filters)

    def get_student(self, student_id: str, class_id: str) -> Optional[Dict]:
        rows = self._get("students", "*", filters={"id": student_id, "class_id": class_id})
        return rows[0] if rows else None

    def create_student(self, data: Dict) -> Dict:
        return self._insert("students", data)

    def update_student(self, student_id: str, class_id: str, data: Dict) -> Dict:
        url = f"{self.url}/rest/v1/students?id=eq.{student_id}&class_id=eq.{class_id}"
        resp = requests.patch(url, headers=self.headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        return result[0] if result else data

    def delete_student(self, student_id: str, class_id: str):
        url = f"{self.url}/rest/v1/students?id=eq.{student_id}&class_id=eq.{class_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()

    # --- Projects ---
    def list_projects(self) -> List[Dict]:
        return self._get("projects", "id,name,path,created_at,last_opened,user_id")

    def get_project(self, project_id: str) -> Optional[Dict]:
        rows = self._get("projects", "*", filters={"id": project_id})
        return rows[0] if rows else None

    def create_project(self, data: Dict) -> Dict:
        return self._insert("projects", data)

    def update_project(self, project_id: str, data: Dict) -> Dict:
        return self._update("projects", "id", project_id, data)

    def delete_project(self, project_id: str):
        self._delete("projects", "id", project_id)


@lru_cache(maxsize=1)
def get_supabase_client() -> SupabaseClient:
    return SupabaseClient()
