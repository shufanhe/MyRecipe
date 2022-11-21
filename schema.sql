drop table if exists recipes;
drop table if exists user;
drop table if exists save_recipe;

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
  content text not null
);
CREATE TABLE save_recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    save_recipe INT,
    recipe_link TEXT NOT NULL
);

create table if not exists calendar(
    recipe_id integer not null,
    date_today date not null,
    cover varbinary not null,
    PRIMARY KEY(date_today),
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT
);