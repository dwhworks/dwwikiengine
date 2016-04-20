create table gold_usd ( 
  date_id date not null,
  final_price numeric(18,2) default 0 not null,
  final_price_type varchar(20) not null,

  constraint pk_gold_usd primary key(date_id)
);

