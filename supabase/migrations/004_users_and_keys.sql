-- 004_users_and_keys.sql
-- Create users and user_keys tables on Supabase for persistent auth

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'student',
    token TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_keys (
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    api_key TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, provider)
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "all_access" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "all_access" ON user_keys FOR ALL USING (true) WITH CHECK (true);
