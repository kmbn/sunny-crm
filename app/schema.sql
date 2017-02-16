drop table if exists users;
create table users (
  id integer primary key autoincrement,
  email varchar,
  password varchar,
  role varchar,
  joined_on varchar,
  status varchar,
  confirmed_on varchar
);


drop table if exists contacts;
create table contacts (
  id integer primary key autoincrement,
  cid integer,
  name varchar,
  note text,
  last_checkin varchar,
  next_checkin varchar,
  next_action varchar,
  created_on varchar,
  creator_id integer,
  foreign key (creator_id) references users(id)
);


drop table if exists updates;
create table updates (
  id integer primary key autoincrement,
  description varchar,
  created_on varchar,
  contact_id integer,
  creator_id integer,
  foreign key (contact_id) references contacts(id),
  foreign key (creator_id) references users(id)
);

drop table if exists achievements;
create table achievements (
  id integer primary key autoincrement,
  achievement varchar,
  created_on varchar,
  creator_id integer,
  foreign key (creator_id) references users(id)
);