-- Template ONLY; review in MySQL administrative console and replace placeholders.
-- Never commit a SQL file with actual database passwords.
CREATE DATABASE IF NOT EXISTS lan_voting CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'lan_voting_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON lan_voting.* TO 'lan_voting_app'@'localhost';
-- For Windows/local TCP 127.0.0.1, grant a separate '127.0.0.1' host account if needed.
-- Use a privileged maintenance account for migrations; do not grant app schema privileges in deployment.
