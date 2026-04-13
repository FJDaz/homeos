-- Mission 298: Lien FK entre students et users
-- Permet à un étudiant d'avoir un compte user distinct (multi-projets perso)
-- SQLite: IF NOT EXISTS not supported on ALTER TABLE — handled by app-level guard

ALTER TABLE students ADD COLUMN user_id TEXT REFERENCES users(id);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
