drop table if exists recipes;
drop table if exists user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

create table recipes (
  id integer primary key autoincrement,
  title text not null,
  category text not null,
  content text not null
);

create table if not exists calendar(
    recipe_id integer not null,
    date_today date not null,
    cover varbinary not null,
    PRIMARY KEY(date_today),
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE RESTRICT
);