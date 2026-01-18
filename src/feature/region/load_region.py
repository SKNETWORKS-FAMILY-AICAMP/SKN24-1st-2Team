from src.database.db_manager import DBManager
from src.region.crawl_region import get_raw_region_data
from src.region.transform_region import transform_region_data

def load_region_info():
    """지역별 충전소 데이터 ETL 프로세스 실행"""
    print("[REGION] 데이터 수집 시작...")
    regions, counts = get_raw_region_data()
    
    print("[REGION] 데이터 가공 시작...")
    transformed = transform_region_data(regions, counts)

    print("[REGION] DB 저장 시작...")
    db = DBManager()
    
    if not db.connect():
        return

    try:
        # DBManager의 커서 활용
        # PK가 지역명이므로 중복 시 개수 업데이트
        query = """
            INSERT INTO region_tbl (region, charger_cnt) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE charger_cnt = VALUES(charger_cnt)
        """
        
        cursor = db.get_cursor()
        cursor.executemany(query, transformed) # 한꺼번에 삽입
        
        db.commit()
        print(f"[REGION] {len(transformed)}개 지역 데이터 저장 완료 ✅")

    except Exception as e:
        print(f"[REGION] 저장 실패 ❌: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_region_info()