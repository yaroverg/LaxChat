
CRT_DB = "create database IF NOT EXISTS DB_NAME_REPLACE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

CRT_USERS = """create table users (
  token VARCHAR(60) PRIMARY KEY,
  email VARCHAR(60),
  display_name VARCHAR(40),
  password VARCHAR(60)
)"""

CRT_CHANNELS = """create table channels (
  channel_name VARCHAR(60) PRIMARY KEY,
  creator_token VARCHAR(60),
  num_messages INT
)"""

CRT_MESSAGES = """create table messages (
  msg_id INT AUTO_INCREMENT PRIMARY KEY,
  channel_name VARCHAR(60),
  reply_id INT,
  author_token VARCHAR(60),
  body TEXT
)"""

CRT_COUNTS = """create table read_counts (
  token VARCHAR(60),
  channel_name VARCHAR(60),
  num_read INT,
  PRIMARY KEY (token, channel_name)
)"""
