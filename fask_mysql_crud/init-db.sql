USE flask_app;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO user (username, email, password) VALUES
('user1', 'user1@example.com', 'dXNlcjFwYXNz'),  -- password: user1pass
('user2', 'user2@example.com', 'dXNlcjJwYXNz'),  -- password: user2pass
('user3', 'user3@example.com', 'dXNlcjNwYXNz');  -- password: user3pass
