create table dw_users (
    dw_username varchar(40) not null,
    dw_password text,
    dw_groups varchar(512),
    show_public_directory integer default 0,
    public_directory_comment text,

    constraint pk_dw_users primary key(dw_username)
);

