"""
Seed database — initial classes/students on HF Space startup.
Run once: creates classes, students, projects from seed data if tables are empty.
"""
import sqlite3
import sys
from pathlib import Path

# Resolve DB_PATH robustly for HF Docker context
DB_DIR = Path(__file__).resolve().parent.parent / "Frontend" / "3. STENCILER" / "db"
DB_PATH = DB_DIR / "projects.db"

def seed():
    # Ensure directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[seed] DB: {DB_PATH}")

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
        id TEXT PRIMARY KEY,
        name TEXT,
        path TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        last_opened TEXT DEFAULT (datetime('now')),
        user_id TEXT
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
                ("le-bellego-margo", "LE BELLEGO Margo", "LE BELLEGO", "Margo"),
                ("overmeer-maelys", "OVERMEER Maëlys", "OVERMEER", "Maelys"),
                ("paulhan-ann-zoe", "PAULHAN Ann-Zoe", "PAULHAN", "Ann-Zoe"),
                ("romary-celio", "ROMARY Celio", "ROMARY", "Celio"),
                ("salle-abigael", "SALLÉ Abigaël", "SALLE", "Abigael"),
                ("schnering-marylou", "SCHNERING Marylou", "SCHNERING", "Marylou"),
                ("serre-lilou", "SERRE Lilou", "SERRE", "Lilou"),
            ],
        },
        {
            "id": "dnmade1-2026",
            "name": "DNMADE1_2026",
            "teacher": "OLN",
            "students": [
                ("blart-samuel", "BLART Samuel", "BLART", "Samuel"),
                ("blin-zoe", "BLIN Zoé", "BLIN", "Zoe"),
                ("calais-jeanne", "CALAIS Jeanne", "CALAIS", "Jeanne"),
                ("chareyron--gamain-lou-ann", "CHAREYRON--GAMAIN Lou-Ann", "CHAREYRON--GAMAIN", "Lou-Ann"),
                ("desseaux-nael", "DESSEAUX Naël", "DESSEAUX", "Nael"),
                ("drelon-oceane", "DRELON Océane", "DRELON", "Oceane"),
                ("ezzyani-sabrine", "EZZYANI Sabrine", "EZZYANI", "Sabrine"),
                ("fadier-aya", "FADIER Aya", "FADIER", "Aya"),
                ("hassaini-riad", "HASSAINI Riad", "HASSAINI", "Riad"),
                ("hurdebourg-noe", "HURDEBOURG Noé", "HURDEBOURG", "Noe"),
                ("lautard-victor", "LAUTARD Victor", "LAUTARD", "Victor"),
                ("le-strat-louane", "LE STRAT Louane", "LE STRAT", "Louane"),
                ("moreau-julie", "MOREAU Julie", "MOREAU", "Julie"),
                ("prodhomme-arthur", "PRODHOMME Arthur", "PRODHOMME", "Arthur"),
                ("rossi-solene", "ROSSI Solène", "ROSSI", "Solene"),
                ("rossi-valentine", "ROSSI Valentine", "ROSSI", "Valentine"),
                ("volant--huguet-sandy", "VOLANT--HUGUET Sandy", "VOLANT--HUGUET", "Sandy"),
                ("warambourg-maia", "WARAMBOURG Maïa", "WARAMBOURG", "Maia"),
            ],
        },
        {
            "id": "dnmade2-2026",
            "name": "DNMADE2_2026",
            "teacher": "OLN",
            "students": [
                ("absolu-alice", "ABSOLU Alice", "ABSOLU", "Alice"),
                ("cazaux-guyon-loula", "CAZAUX-GUYON Loula", "CAZAUX-GUYON", "Loula"),
                ("dodier-zoe", "DODIER Zoé", "DODIER", "Zoe"),
                ("dulhoste-emma", "DULHOSTE Emma", "DULHOSTE", "Emma"),
                ("hay-lya", "HAY Lya", "HAY", "Lya"),
                ("hervieux-domitille", "HERVIEUX Domitille", "HERVIEUX", "Domitille"),
                ("marie-eleonore", "MARIE Eléonore", "MARIE", "Eleonore"),
                ("mkadara-nasma", "MKADARA Nasma", "MKADARA", "Nasma"),
                ("pouillot-alix", "POUILLOT Alix", "POUILLOT", "Alix"),
                ("sauvage-chloe", "SAUVAGE Chloé", "SAUVAGE", "Chloe"),
                ("viard-sixtine", "VIARD Sixtine", "VIARD", "Sixtine"),
                ("wehrle-evan", "WEHRLE Evan", "WEHRLE", "Evan"),
                ("zaffiroff-adeline", "ZAFFIROFF Adeline", "ZAFFIROFF", "Adeline"),
            ],
        },
    ]

    total_students = 0
    total_projects = 0

    for cls in SEED_CLASSES:
        cur.execute("INSERT OR IGNORE INTO classes (id, name, teacher) VALUES (?, ?, ?)",
                    (cls["id"], cls["name"], cls["teacher"]))
        for sid, display, last, first in cls["students"]:
            project_id = f"{cls['id']}-{sid}"
            project_path = f"projects/{project_id}"
            cur.execute("INSERT OR IGNORE INTO students (id, class_id, display, last_name, first_name, project_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (sid, cls["id"], display, last, first, None))
            cur.execute("INSERT OR IGNORE INTO projects (id, name, path, user_id) VALUES (?, ?, ?, ?)",
                        (project_id, display, project_path, sid))
            cur.execute("UPDATE students SET project_id = ? WHERE id = ?",
                        (project_id, sid))
            total_students += 1
            total_projects += 1

    conn.commit()
    conn.close()
    print(f"[seed] Done. {total_students} students, {total_projects} projects created.")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"[seed] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
