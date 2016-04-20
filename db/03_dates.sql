create table dates (
  date_id date not null,
  year_num integer,
  month_num integer,
  month_day_num integer,
  year_day_num integer,
  week_num_mon integer,
  week_num_sun integer,
  weekday_num_mon integer,
  weekday_num_sun integer,
  week_first_date_mon date,
  week_last_date_mon date,
  week_first_date_sun date,
  week_last_date_sun date,
  month_name_en varchar(40),
  month_name_short_en varchar(10),
  month_name_ru varchar(40),
  month_name_short_ru varchar(10),
  weekday_name_en varchar(20),
  weekday_name_short_en varchar(10),
  weekday_name_ru varchar(20),
  weekday_name_short_ru varchar(10),

  constraint pk_dates primary key(date_id)
);

