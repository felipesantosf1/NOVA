-- Uma sessão é uma conversa.
CREATE TABLE IF NOT EXISTS sessions (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cada mensagem pertence a uma sessão.
CREATE TABLE IF NOT EXISTS messages (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id  BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Deixa rápida a busca das últimas mensagens de uma sessão.
CREATE INDEX IF NOT EXISTS idx_messages_session
    ON messages (session_id, id);