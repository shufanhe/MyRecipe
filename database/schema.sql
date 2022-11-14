drop table if exists recipes;
drop table if exists user;
drop table if exists reviews;
drop table if exists like_recipe;
drop table if exists created_recipes;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

create table recipes (
  id integer primary key autoincrement,
  user_id INT NOT NULL,
  title text not null,
  category text not null,
  content text not null,
  likes INTEGER DEFAULT 0 NOT NULL,
  review text,
  FOREIGN KEY(user_id) REFERENCES user(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE reviews (
    recipe_id INTEGER NOT NULL,
    review TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE like_recipe (
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    liked INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(user_id) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE created_recipes (
    user_id INTEGER NOT NULL,
    title text not null,
    category text not null,
    content text not null,
    likes INTEGER DEFAULT 0 NOT NULL,
    review text,
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

