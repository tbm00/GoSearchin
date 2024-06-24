CREATE DATABASE IF NOT EXISTS usersDB;

USE usersDB;

CREATE TABLE IF NOT EXISTS Location (
  location_id INT AUTO_INCREMENT PRIMARY KEY,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  weather_data JSON
);

CREATE TABLE IF NOT EXISTS Accounts (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  location_id INT,
  FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE IF NOT EXISTS search_queries (
  query_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  query_text VARCHAR(255) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES Accounts(user_id)
);

CREATE TABLE IF NOT EXISTS results (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  query_id INT,
  result_text TEXT,
  FOREIGN KEY (query_id) REFERENCES search_queries(query_id)
);
