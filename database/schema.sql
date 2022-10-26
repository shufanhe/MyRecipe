drop table if exists recipe;
create table recipe (
  id integer primary key autoincrement,
  title text not null,
  category text not null,
  content text not null
);