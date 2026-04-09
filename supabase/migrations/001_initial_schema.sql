-- 001_initial_schema.sql (v2 — match class_router column names)
CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    subject TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS students (
    id TEXT NOT NULL,
    class_id TEXT REFERENCES classes(id),
    display TEXT,
    nom TEXT,
    prenom TEXT,
    project_id TEXT,
    milestone INTEGER DEFAULT 0,
    progress INTEGER DEFAULT 0,
    PRIMARY KEY (id, class_id)
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT,
    path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_opened TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT
);

ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "all_access" ON classes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "all_access" ON students FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "all_access" ON projects FOR ALL USING (true) WITH CHECK (true);
