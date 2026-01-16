create database if not exists khsdb;
grant all privileges on khsdb.* to ohgiraffers@'%';

use khsdb;

-- 기존 테이블이 있다면 삭제하여 초기화
drop table if exists region_tbl;

-- 테이블 생성 (region이 PK)
create table region_tbl (
    region varchar(50) primary key,
    charger_cnt int not null
);