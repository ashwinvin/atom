CREATE DATABASE analyst;
\c analyst ;

CREATE TABLE errors (id SERIAL PRIMARY KEY, 
                    url TEXT NOT NULL,
                    type TEXT NOT NULL,
                    fixed BOOL NOT NULL);
