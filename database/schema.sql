drop table if exists recipes;
drop table if exists user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

create table recipes (
  id integer primary key autoincrement,
  title text not null,
  category text not null,
  content text not null,
  likes int,
  review text
);

CREATE TABLE if not exists reviews (
    recipe_id INT NOT NULL,
    likes INT,
    review TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE if not exists like_recipe (
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    liked INT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(user_id) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE if not exists save_recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    save_recipe INT,
    recipe_link TEXT NOT NULL
);

CREATE TABLE if not exists calendar(
    date_today TEXT PRIMARY KEY,
    recipe_id integer not null,
    cover varbinary not null,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

