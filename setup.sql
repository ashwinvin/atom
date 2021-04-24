CREATE TABLE IF NOT EXISTS errors (
    id              SERIAL PRIMARY KEY,
    url             TEXT NOT NULL,
    type            TEXT NOT NULL,
    msg             TEXT NOT NULL,
    user            BIGINT NOT NULL,
    fixed           BOOL NOT NULL
);

CREATE TABLE IF NOT EXISTS guilds (
    id              SERIAL PRIMARY KEY,
    gid             BIGINT NOT NULL UNIQUE,
    prefix          TEXT DEFAULT '#' NOT NULL
);

CREATE TABLE IF NOT EXISTS samp (
    id             INT PRIMARY KEY REFERENCES guilds(id) ON DELETE CASCADE,
    samp_ip        TEXT,
    samp_port      INT
);


CREATE TABLE IF NOT EXISTS minecraft (
    id            INT PRIMARY KEY REFERENCES guilds(id) ON DELETE CASCADE,
    mc_ip         TEXT,
    mc_port       INT
);

CREATE TABLE IF NOT EXISTS tags (
    id            SERIAL PRIMARY KEY,
    gid           BIGINT NOT NULL REFERENCES guilds(gid) ON DELETE CASCADE,
    author        BIGINT NOT NULL,
    name          TEXT NOT NULL,
    content       TEXT NOT NULL,
    public        BOOLEAN DEFAULT false,
    allowed       BIGINT []
);
