drop table if exists recipe;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
create table recipe (
  id integer primary key autoincrement,
  title text not null,
  category text not null,
  content text not null
);