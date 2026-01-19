"""
차량 정보 서비스 모듈
DB에서 차량 정보를 조회하는 함수 제공
"""
from src.database.db_manager import DBManager


def get_car_info_list(fuel_type=None, maker=None):
    """
    차량 정보 목록 조회
    
    Args:
        fuel_type: 연료 타입 필터 (예: "전기", "LPG")
        maker: 제조사 필터 (예: "기아", "현대")
    
    Returns:
        list[dict]: 차량 정보 딕셔너리 리스트
    """
    db = DBManager()
    if not db.connect():
        return []
    
    try:
        cursor = db.get_cursor()
        
        query = """
            SELECT car_id, fuel_type, name, maker, size, capacity, h_power, max_fuel,
                   cx_efc, ct_efc, hw_efc, max_dist, price, maintenance_cost, image
            FROM car_info_tbl
        """
        
        conditions = []
        params = []
        
        if fuel_type:
            conditions.append("fuel_type = %s")
            params.append(fuel_type)
        
        if maker:
            conditions.append("maker = %s")
            params.append(maker)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY price ASC"
        
        cursor.execute(query, tuple(params))
        
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in results]
    
    except Exception as e:
        print(f"[CAR_INFO_SERVICE] 차량 정보 조회 실패 ❌: {e}")
        return []
    finally:
        db.close()


def get_car_info_by_id(car_id):
    """
    특정 차량 상세 정보 조회
    
    Args:
        car_id: 차량 ID
    
    Returns:
        dict: 차량 정보 딕셔너리 또는 None
    """
    db = DBManager()
    if not db.connect():
        return None
    
    try:
        cursor = db.get_cursor()
        
        query = """
            SELECT car_id, fuel_type, name, maker, size, capacity, h_power, max_fuel,
                   cx_efc, ct_efc, hw_efc, max_dist, price, maintenance_cost, image
            FROM car_info_tbl
            WHERE car_id = %s
        """
        
        cursor.execute(query, (car_id,))
        
        columns = [desc[0] for desc in cursor.description]
        result = cursor.fetchone()
        
        if result:
            return dict(zip(columns, result))
        return None
    
    except Exception as e:
        print(f"[CAR_INFO_SERVICE] 차량 정보 조회 실패 ❌: {e}")
        return None
    finally:
        db.close()


def get_car_info_by_family(family_name):
    """
    차량 계열별 정보 조회 (봉고/포터)
    
    Args:
        family_name: 차량 계열명 (예: "봉고", "포터")
    
    Returns:
        list[dict]: 차량 정보 딕셔너리 리스트
    """
    db = DBManager()
    if not db.connect():
        return []
    
    try:
        cursor = db.get_cursor()
        
        query = """
            SELECT car_id, fuel_type, name, maker, size, capacity, h_power, max_fuel,
                   cx_efc, ct_efc, hw_efc, max_dist, price, maintenance_cost, image
            FROM car_info_tbl
            WHERE name LIKE %s
            ORDER BY price ASC
        """
        
        cursor.execute(query, (f"%{family_name}%",))
        
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in results]
    
    except Exception as e:
        print(f"[CAR_INFO_SERVICE] 차량 정보 조회 실패 ❌: {e}")
        return []
    finally:
        db.close()
