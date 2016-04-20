[home](../../) /
[docs](../) /
[database](./) /
dates

`dates`
-------------

Dates dimension table. Contains all dates since Jan 1st, 1900 to Dec 31st, 2050


name                | type	      | null | pk  | comments 
--------------------|-------------|------|-----|----------------------
date_id             | date        | NO   | YES | Date without time
year_num            | integer     | NO   |     | Year number
month_num           | integer     | NO   |     | Month number 1 to 12
month_day_num       | integer     | NO   |     | Day number in a month 1 to 31
year_day_num        | integer     | NO   |     | Day number in a year 1 to 365 (366)
week_num_mon        | integer     | NO   |     | Week number in a year. Week starts on Monday
week_num_sun        | integer     | NO   |     | Week number in a year. Week starts on Sunday
weekday_num_mon     | integer     | NO   |     | Week day number. Monday - 1, Sunday - 7
weekday_num_sun     | integer     | NO   |     | Week day number. Sunday - 1, Saturday - 7
week_first_date_mon | date        | NO   |     | First date of current week. Week starts on Monday
week_last_date_mon  | date        | NO   |     | Last date of current week. Week ends on Sunday
week_first_date_sun | date        | NO   |     | First date of current week. Week starts on Sunday
week_last_date_sun  | date        | NO   |     | Last date of current week. Week ends on Saturday
month_name_en       | varchar(40) | NO   |     | Month name in English
month_name_short_en | varchar(10) | NO   |     | Short month name in English. JAN, FEB etc.
month_name_ru       | varchar(40) | NO   |     | Month name in Russian
month_name_short_ru | varchar(10) | NO   |     | Short month name in Russian.
weekday_name_en     | varchar(20) | NO   |     | Weekday name in English
weekday_name_short_en | varchar(10) | NO |     | Short weekday name in English - SUN, MON etc.
weekday_name_ru     | varchar(20) | NO   |     | Weekday name in Russian
weekday_name_short_ru | varchar(10) | NO |     | Short weekday name in Russian
weekday_name_ru_rp  | varchar(40) | NO   |     | Weekday name in Russian in genitive
month_name_ru_rp    |varchar(40)  | NO   |     | Month name in Russian in genitive

----------------------------------------------------------------------

[View page source](dates.markdown)
