use khsdb;

-- 기존 테이블이 있다면 삭제하여 초기화
drop table if exists fuel_tbl;

-- 테이블 생성 (fuel_tbl)
create table fuel_tbl (
	fuel_type varchar(50) primary key,
    fuel_cost float not null
);
    