-- Create database
CREATE DATABASE IF NOT EXISTS finhabit_db;
USE finhabit_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Create habits table
CREATE TABLE IF NOT EXISTS habits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    frequency VARCHAR(50),
    target_amount INT,
    progress INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;

INSERT INTO users (name, email, password, is_admin)
VALUES ('Admin', 'admin@gmail.com', '123', 1);