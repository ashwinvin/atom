CREATE DATABASE analyst;
\c analyst ;

CREATE TABLE errors (id SERIAL PRIMARY KEY, 
                    url TEXT NOT NULL,
                    type TEXT NOT NULL,
                    fixed BOOL NOT NULL);

CREATE TABLE guilds (id SERIAL PRIMARY KEY,
                    gid INT NOT NULL,
                    samp TEXT NOT NULL,
                    sbchannel INT NOT NULL,
                    sbmin INT NOT NULL);
