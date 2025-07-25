-- Create database if it doesn't exist
SELECT 'CREATE DATABASE backend_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'backend_db');

-- Connect to the database
\c backend_db;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables will be created by SQLAlchemy when services start