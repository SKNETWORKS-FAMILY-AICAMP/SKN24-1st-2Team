from src.database.db_manager import DBManager

def get_fuel_list(fuel_type=None):
    db = DBManager()
    if not db.connect():
        return[]
    try:
        cursor = db.get_cursor()

        query = "SELECT fuel_type, fuel_cost FROM fuel_tbl"
        params = ()

        # 매개변수가 주어졌을 경우
        if fuel_type:
            query += " WHERE fuel_type = %s"
            params = (fuel_type,)

        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()

        return [dict(zip(columns, row)) for row in results]
    
    except Exception as e:
        print(f"[FUEL_SERVICE] 연료 테이블 조회 실패 ❌: {e}")
        return []
    finally:
        db.close()