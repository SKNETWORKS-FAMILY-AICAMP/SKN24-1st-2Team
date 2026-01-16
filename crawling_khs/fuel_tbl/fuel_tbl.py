import mysql.connector
import crawling_fuel_cost

# 크롤링 리스트 호울
avg_disel_cost, avg_lpg_cost, avg_ev_cost = crawling_fuel_cost.cost_fuel()
fuel_cost = [avg_disel_cost, avg_lpg_cost, avg_ev_cost]
fuel_type = ['Disel', 'LPG', 'EV']

# DB 연결
connection = mysql.connector.connect(
    host='localhost',       # MySQL 서버 주소 (ip)
    user='ohgiraffers',     # 사용자 이름
    password='ohgiraffers', # 비밀번호
    database='khsdb'        # 데이터베이스 이름(임시)
)

cursor = connection.cursor()

sql_insert = 'insert into fuel_tbl (fuel_type, fuel_cost) values (%s, %s)'

for i in range(3):
    values = (fuel_type[i], fuel_cost[i])
    cursor.execute(sql_insert, values)


connection.commit()
cursor.close()
connection.close()