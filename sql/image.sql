CREATE DATABASE IF NOT EXISTS test;

USE test;

CREATE TABLE IF NOT EXISTS image (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_url VARCHAR(255) NOT NULL UNIQUE,
    features BLOB NOT NULL,
    shape BLOB NOT NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;