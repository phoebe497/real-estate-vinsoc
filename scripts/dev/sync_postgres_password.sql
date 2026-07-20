\getenv db_user POSTGRES_USER
\getenv db_password POSTGRES_PASSWORD
ALTER ROLE :"db_user" WITH PASSWORD :'db_password';
