from src.database.db_manager import DBManager
from src.fuel.crawl_fuel import get_raw_fuel_data
from src.fuel.transform_fuel import transform_fuel_data

def load_fuel_info():
    """연료 데이터 ETL 프로세스 실행"""
    print("[FUEL] 데이터 수집 시작...")
    raw = get_raw_fuel_data()
    
    print("[FUEL] 데이터 가공 시작...")
    transformed = transform_fuel_data(raw)

    print("[FUEL] DB 저장 시작...")
    db = DBManager()
    
    if not db.connect():
        return

    try:
        # DBManager의 execute 메서드 활용
        query = "INSERT INTO fuel_tbl (fuel_type, fuel_cost) VALUES (%s, %s) ON DUPLICATE KEY UPDATE fuel_cost = VALUES(fuel_cost)"
        
        cursor = db.get_cursor()
        cursor.executemany(query, transformed) # 여러 데이터를 한번에 삽입
        
        db.commit()
        print(f"[FUEL] {len(transformed)}건 저장 완료 ✅")

    except Exception as e:
        print(f"[FUEL] 저장 실패 ❌: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    load_fuel_info()