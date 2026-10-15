-- Run this in your Supabase SQL Editor (https://supabase.com → SQL Editor)

-- Chat history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    message TEXT NOT NULL,
    command_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contacts (for email/whatsapp - Phase 3)
CREATE TABLE IF NOT EXISTS contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    platform TEXT CHECK (platform IN ('email', 'whatsapp')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User preferences
CREATE TABLE IF NOT EXISTS settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Command execution logs
CREATE TABLE IF NOT EXISTS command_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    command TEXT NOT NULL,
    parameters JSONB,
    status TEXT CHECK (status IN ('success', 'error')),
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vision snapshots
CREATE TABLE IF NOT EXISTS snapshots (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    objects JSONB,
    description TEXT,
    image_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_command_logs_created_at ON command_logs(created_at DESC);

-- Enable RLS (Row Level Security) - recommended for production
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE command_logs ENABLE ROW LEVEL SECURITY;

-- Policies: allow all operations with anon key (for local app)
CREATE POLICY "Allow all on conversations" ON conversations FOR ALL USING (true);
CREATE POLICY "Allow all on contacts" ON contacts FOR ALL USING (true);
CREATE POLICY "Allow all on settings" ON settings FOR ALL USING (true);
CREATE POLICY "Allow all on snapshots" ON snapshots FOR ALL USING (true);
CREATE POLICY "Allow all on command_logs" ON command_logs FOR ALL USING (true);
