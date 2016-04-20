create table curr_rates(
    date_id date not null,
    curr_code varchar(10) not null,
    nomination integer,
    current_rate numeric(18,4),
    current_rate_type varchar(40),
    rate_minus_1 numeric(18,4),
    rate_minus_30 numeric(18,4),
    rate_minus_60 numeric(18,4),
    rate_minus_90 numeric(18,4),
    rate_minus_180 numeric(18,4),
    rate_minus_360 numeric(18,4),
    rate_minus_720 numeric(18,4),
    constraint pk_curr_rates primary key(date_id,curr_code)
);

