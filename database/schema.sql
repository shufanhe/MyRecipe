drop table if exists recipe;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);
create table recipe (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  content TEXT NOT NULL
);
CREATE TABLE save_recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    save_recipe INT,
    recipe_link TEXT NOT NULL
);
create table calendar (
    recipe_id integer not null,
    date_today date not null,
    cover varbinary not null,
    PRIMARY KEY(date_today),
    FOREIGN KEY(recipe_id) REFERENCES recipe(id) ON UPDATE CASCADE ON DELETE RESTRICT
);