"""
Seed database — initial classes/students on HF Space startup.
Run once: creates classes, students, subjects from seed data if tables are empty.
"""
import sqlite3
import uuid
import hashlib
import os
from pathlib import Path

# Sur HF: /app/Frontend/3. STENCILER/db/projects.db
# En local: AETHERFLOW/Frontend/3. STENCILER/db/projects.db
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "Frontend" / "3. STENCILER" / "db" / "projects.db"


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


SEED_CLASSES = [
    {
        "id": "dnamde3",
        "name": "DNMADE3_2026",
        "teacher": "OLN",
        "students": [
            ("darnoux-cyrielle", "DARNOUX Cyrielle", "DARNOUX", "Cyrielle"),
            ("delaplace-juliette", "DELAPLACE Juliette", "DELAPLACE", "Juliette"),
            ("dumont-hugo", "DUMONT Hugo", "DUMONT", "Hugo"),
            ("gwazda-charline", "GWAZDA Charline", "GWAZDA", "Charline"),
            ("hiver-lyse", "HIVER Lyse", "HIVER", "Lyse"),
            ("martinez-lea", "MARTINEZ Lea", "MARTINEZ", "Lea"),
            ("rousseau-maxime", "ROUSSEAU Maxime", "ROUSSEAU", "Maxime"),
        ],
    },
    {
        "id": "dnmade2-2026",
        "name": "DNMADE2_2026",
        "teacher": "OLN",
        "students": [
            ("blart-samuel", "BLART Samuel", "BLART", "Samuel"),
        ],
    },
    {
        "id": "dnmade1-2026",
        "name": "DNMADE1_2026",
        "teacher": "OLN",
        "students": [],
    },
]

SEED_USERS = [
    {"id": str(uuid.uuid4()), "name": "FJD", "role": "admin", "token": str(uuid.uuid4())},
    {"name": "DNMADE_3_2026", "role": "student", "class_id": "dnamde3"},
    {"name": "DNMADE2_2026", "role": "student", "class_id": "dnmade2-2026"},
    {"name": "DNMADE1_2026", "role": "student", "class_id": "dnmade1-2026"},
]


def seed():
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Check if already seeded
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")
    if cur.fetchone():
        cur.execute("SELECT COUNT(*) FROM classes")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"[seed] DB already has {count} classes, skipping.")
            conn.close()
            return

    print("[seed] Creating tables and seeding data...")

    # Create tables
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, name TEXT, role TEXT, token TEXT,
        created_at TEXT DEFAULT (datetime('now')), password_hash TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS user_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, provider TEXT,
        api_key TEXT, FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY, name TEXT, teacher TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS students (
        id TEXT, class_id TEXT, display TEXT, last_name TEXT,
        first_name TEXT, project_id TEXT, progress INTEGER DEFAULT 0,
        PRIMARY KEY (id, class_id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY, name TEXT, student_id TEXT,
        class_id TEXT, created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(class_id) REFERENCES classes(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY, class_id TEXT, title TEXT, content TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(class_id) REFERENCES classes(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, user_id TEXT, messages TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    # Seed classes
    for cls in SEED_CLASSES:
        cur.execute("INSERT OR IGNORE INTO classes (id, name, teacher) VALUES (?, ?, ?)",
                    (cls["id"], cls["name"], cls["teacher"]))
        for sid, display, last, first in cls["students"]:
            project_id = f"{cls['id']}-{sid}"
            cur.execute("INSERT OR IGNORE INTO students (id, class_id, display, last_name, first_name, project_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (sid, cls["id"], display, last, first, project_id))

    # Seed admin user
    admin_token = str(uuid.uuid4())
    cur.execute("INSERT OR IGNORE INTO users (id, name, role, token) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), "FJD", "admin", admin_token))

    conn.commit()
    conn.close()
    print(f"[seed] Done. Created {len(SEED_CLASSES)} classes, {sum(len(c['students']) for c in SEED_CLASSES)} students.")
    print(f"[seed] Admin token: {admin_token}")


if __name__ == "__main__":
    seed()
