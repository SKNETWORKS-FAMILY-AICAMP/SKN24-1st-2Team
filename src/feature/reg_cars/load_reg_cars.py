from src.database.db_manager import DBManager
import pandas as pd
# from dotenv import load_dotenv
# load_dotenv()

# db
db = DBManager()
if not db.connect():
    print("!!! DB 연결 실패 !!!")

cursor = db.cursor

# csv
csv_path = 'data/processed/registered_cars/processed_registered_cars.csv'
df = pd.read_csv(csv_path)


insert_sql = """
INSERT INTO cnt_tbl (fuel_type, region, date, cnt) VALUES (%s, %s, %s, %s)
"""

try:
    print("[REG CARS] DB 저장 시작...")
    for i in range(len(df)):
        value = (df['fuel_type'][i], df['region'][i], int(df['date'][i]), int(df['cnt'][i]))
        db.execute(insert_sql, value)

    db.commit()
    print("데이터 삽입 완료 ✅")

except Exception as e:
    print(f"!!! 삽입 실패: {e} !!!")
    db.rollback()

finally:
    db.close()
    print("DB 연결 종료.")

   