"""
봉고 차량 정보 데이터 로드 모듈
변환된 데이터를 DB에 저장
"""
from src.database.db_manager import DBManager
from src.feature.cars_info.bongo.transform_bongo import transform_bongo_data


def load_bongo_info():
    """봉고 차량 데이터 ETL 프로세스 실행"""
    print("[BONGO] 데이터 가공 시작...")
    
    try:
        transformed = transform_bongo_data()
        
        if not transformed:
            print("[BONGO] 변환된 데이터가 없습니다.")
            return
        
        print(f"[BONGO] {len(transformed)}건의 데이터 변환 완료")
        
        print("[BONGO] DB 저장 시작...")
        db = DBManager()
        
        if not db.connect():
            print("[BONGO] DB 연결 실패")
            return
        
        try:
            # INSERT 쿼리
            query = """
                INSERT INTO car_info_tbl (
                    fuel_type, name, maker, size, capacity, h_power, max_fuel,
                    cx_efc, ct_efc, hw_efc, max_dist, price, maintenance_cost, image
                ) VALUES (
                    %(fuel_type)s, %(name)s, %(maker)s, %(size)s, %(capacity)s, %(h_power)s, %(max_fuel)s,
                    %(cx_efc)s, %(ct_efc)s, %(hw_efc)s, %(max_dist)s, %(price)s, %(maintenance_cost)s, %(image)s
                )
            """
            
            cursor = db.get_cursor()
            
            # 각 데이터 삽입
            success_count = 0
            for data in transformed:
                if db.execute(query, data):
                    success_count += 1
                else:
                    print(f"[BONGO] 데이터 삽입 실패: {data.get('name', 'Unknown')}")
            
            db.commit()
            print(f"[BONGO] {success_count}/{len(transformed)}건 저장 완료 ✅")
            
        except Exception as e:
            print(f"[BONGO] 저장 실패 ❌: {e}")
            db.rollback()
            raise
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"[BONGO] 처리 중 오류 발생 ❌: {e}")
        raise


if __name__ == "__main__":
    load_bongo_info()
