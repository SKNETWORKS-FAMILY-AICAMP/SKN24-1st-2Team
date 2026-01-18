from src.database.db_manager import DBManager

def get_region_list(region=None):
    db = DBManager()
    if not db.connect():
        return[]
    try:
        cursor = db.get_cursor()

        query = "SELECT region, charger_cnt FROM region_tbl"
        params = ()

        # 매개변수가 주어졌을 경우
        if region:
            query += " WHERE region = %s"
            params = (region,)

        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()

        return [dict(zip(columns, row)) for row in results]
    
    except Exception as e:
        print(f"[REGION_SERVICE] 지역 테이블 조회 실패 ❌: {e}")
        return []
    finally:
        db.close()