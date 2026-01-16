import mysql.connector
import crawling_charger_cnt

# 크롤링 리스트 호출
region_list, charger_cnt_list = crawling_charger_cnt.crawling()

# DB 연결
connection = mysql.connector.connect(
    host='localhost',       # MySQL 서버 주소 (ip)
    user='ohgiraffers',     # 사용자 이름
    password='ohgiraffers', # 비밀번호
    database='khsdb'        # 데이터베이스 이름(임시)
)

cursor = connection.cursor()

sql_insert = 'insert into region_tbl (region, charger_cnt) values (%s, %s)'

for i in range(len(region_list)):
    values = (region_list[i], charger_cnt_list[i])
    cursor.execute(sql_insert, values)

connection.commit()
cursor.close()
connection.close()