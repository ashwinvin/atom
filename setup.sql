CREATE DATABASE analyst;
\c analyst ;

CREATE TABLE errors (id SERIAL PRIMARY KEY, 
                    url TEXT NOT NULL,
                    type TEXT NOT NULL,
                    fixed BOOL NOT NULL);

CREATE TABLE guilds (id SERIAL PRIMARY KEY,
                    gid INT NOT NULL UNIQUE,
                    samp_ip TEXT,
                    samp_port INT,
                    sbchannel INT ,
                    sbmin INT);
