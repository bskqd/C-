create user ac_user with encrypted password 'pass';
create database communication OWNER ac_user;
create database itcs_main OWNER ac_user;
