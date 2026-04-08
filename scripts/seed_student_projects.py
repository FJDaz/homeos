"""
M271 — Seed projets étudiants
Crée un projet dans la table `projects` pour chaque élève sans project_id,
et met à jour `students.project_id`.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "db" / "projects.db"


def seed_projects():
    if not DB_PATH.exists():
        print(f"[seed] DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Fix Lilou (wrong project_id)
    cur.execute("UPDATE students SET project_id = NULL WHERE id = 'serre-lilou'")

    # Get all students without project
    cur.execute("""
        SELECT id, display, class_id 
        FROM students 
        WHERE project_id IS NULL OR project_id = ''
        ORDER BY class_id, id
    """)
    students = cur.fetchall()

    # Ensure projects table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT,
            class_id TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    created = 0
    for student_id, display, class_id in students:
        project_id = f"{class_id}-{student_id}"
        project_name = f"{display}" if display else student_id

        # Create project
        project_path = f"projects/{project_id}"
        cur.execute(
            "INSERT OR IGNORE INTO projects (id, name, path, user_id) VALUES (?, ?, ?, ?)",
            (project_id, project_name, project_path, student_id)
        )

        # Link student to project
        cur.execute(
            "UPDATE students SET project_id = ? WHERE id = ?",
            (project_id, student_id)
        )
        created += 1

    conn.commit()

    # Verify
    cur.execute("""
        SELECT s.id, s.display, s.class_id, s.project_id
        FROM students s
        ORDER BY s.class_id, s.id
    """)
    total = 0
    with_project = 0
    for sid, display, class_id, pid in cur.fetchall():
        total += 1
        status = "✅" if pid else "❌"
        if pid:
            with_project += 1
        print(f"  {status} {sid:30s} → {pid or 'NO PROJECT'}")

    print(f"\n[seed] {created} projets créés")
    print(f"[seed] {with_project}/{total} élèves avec projet")

    conn.close()


if __name__ == "__main__":
    seed_projects()
