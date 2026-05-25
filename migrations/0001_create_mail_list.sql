CREATE TABLE IF NOT EXISTS email_list (
    id              SERIAL PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    signed_up_at    TIMESTAMPTZ DEFAULT NOW()
);