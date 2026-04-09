-- 001_initial_schema.sql
-- Create tables for AetherFlow class/student/project management

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
    last_name TEXT,
    first_name TEXT,
    project_id TEXT,
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

-- Enable Row Level Security
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Allow public read for now (can be tightened later)
CREATE POLICY "classes_read_all" ON classes FOR SELECT USING (true);
CREATE POLICY "students_read_all" ON students FOR SELECT USING (true);
CREATE POLICY "projects_read_all" ON projects FOR SELECT USING (true);
CREATE POLICY "classes_all" ON classes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "students_all" ON students FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "projects_all" ON projects FOR ALL USING (true) WITH CHECK (true);
