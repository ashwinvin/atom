CREATE TABLE IF NOT EXISTS errors (
    id              SERIAL PRIMARY KEY,
    url             TEXT NOT NULL,
    type            TEXT NOT NULL,
    msg             TEXT NOT NULL,
    author          BIGINT NOT NULL,
    fixed           BOOL NOT NULL
);

CREATE TABLE IF NOT EXISTS guilds (
    id              SERIAL PRIMARY KEY,
    gid             BIGINT NOT NULL UNIQUE,
    prefix          TEXT DEFAULT '#' NOT NULL,
    kicked          TIMESTAMP
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
    creation      TIMESTAMP NOT NULL,
    author        BIGINT NOT NULL,
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    public        BOOLEAN DEFAULT false,
    allowed       BIGINT [],
    uses          INT DEFAULT 0 NOT NULL 
);
