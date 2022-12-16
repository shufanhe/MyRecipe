drop table if exists recipes;
drop table if exists user_image;
drop table if exists user_summary;
drop table if exists user;
drop table if exists reviews;
drop table if exists like_recipe;
drop table if exists notifications;
drop table if exists save_recipe;
drop table if exists save_author;
drop table if exists tag_name;
drop table if exists tags;
drop table if exists calendar;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    verified TEXT NOT NULL,
    OTP_code TEXT NOT NULL
);

CREATE TABLE user_image (
    user_id INTEGER NOT NULL,
    image TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(username)
);

CREATE TABLE user_summary (
    user_id INTEGER NOT NULL,
    summary TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(username) ON UPDATE CASCADE ON DELETE CASCADE
);

create table recipes (
  id integer primary key autoincrement,
  user_id INT NOT NULL,
  title text not null,
  category text not null,
  content text not null,
  posted_date text not null,
  likes INTEGER DEFAULT 0 NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);


CREATE TABLE reviews (
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    review TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE like_recipe (
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES user(id)
);


CREATE TABLE if not exists save_recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    recipe_id INTEGER NOT NULL
);

CREATE TABLE notifications (
    to_user TEXT NOT NULL,
    from_user TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_date TEXT NOT NULL,
    action_time TEXT NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY(to_user) REFERENCES user(username) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(from_user) REFERENCES user(username) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE save_author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    user TEXT NOT NULL
);

CREATE TABLE if not exists calendar(
    date_today TEXT PRIMARY KEY,
    recipe_id integer not null,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
);

CREATE TABLE if not exists tag_name(
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL
);

INSERT INTO tag_name (tag_name)
VALUES ('Gluten Free'),
       ('Dairy Free'),
       ('Nut Free'),
       ('Vegan'),
       ('Vegetarian');

CREATE TABLE if not exists tags(
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(tag_id) REFERENCES tag_name(tag_id)
);

CREATE TABLE IF NOT EXISTS recipe_image (
  recipe_id INTEGER NOT NULL,
  image TEXT NOT NULL,
  FOREIGN KEY(recipe_id) REFERENCES recipes(id)

);