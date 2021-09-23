-- mysql -usomeUser -psomePass < 20200304T184700-create_tables.sql

use lax_db;

create table users (
  token VARCHAR(60) PRIMARY KEY,
  email VARCHAR(60),
  display_name VARCHAR(40),
  password VARCHAR(60)
);

create table channels (
  channel_name VARCHAR(60) PRIMARY KEY,
  creator_token VARCHAR(60),
  num_messages INT
);

create table messages (
  msg_id INT AUTO_INCREMENT PRIMARY KEY,
  channel_name VARCHAR(60),
  reply_id INT,
  author_token VARCHAR(60),
  body TEXT
);

create table read_counts (
  token VARCHAR(60),
  channel_name VARCHAR(60),
  num_read INT,
  PRIMARY KEY (token, channel_name)
);
