-- M283a: Workspaces + Entitlements
-- Multi-tenancy soft : chaque utilisateur appartient à un workspace
-- Les plans (FREE/PRO/MAX) sont liés au workspace

-- 1. Workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'FREE', -- FREE, PRO, MAX
    owner_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Workspace members (links users to workspaces)
CREATE TABLE IF NOT EXISTS workspace_members (
    user_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    role_in_workspace TEXT NOT NULL DEFAULT 'member', -- owner, admin, member, viewer
    PRIMARY KEY (user_id, workspace_id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- 3. Add plan column to users (default FREE, overridden by workspace plan)
ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'FREE';
ALTER TABLE users ADD COLUMN workspace_id TEXT;

-- 4. Seed: create default workspaces for existing users
-- Each existing user gets a personal workspace
INSERT OR IGNORE INTO workspaces (id, name, plan, owner_id)
SELECT 'ws_' || id, 'Workspace ' || name, 'FREE', id
FROM users
WHERE 'ws_' || id NOT IN (SELECT id FROM workspaces);

-- 5. Seed: link all existing users to their personal workspace
INSERT OR IGNORE INTO workspace_members (user_id, workspace_id, role_in_workspace)
SELECT id, 'ws_' || id, 'owner'
FROM users
WHERE id NOT IN (SELECT user_id FROM workspace_members);

-- 6. Update users with workspace_id
UPDATE users SET workspace_id = 'ws_' || id WHERE workspace_id IS NULL;
