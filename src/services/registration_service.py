from src.database.db_manager import DBManager
import pandas as pd

def get_registration_count_list():
    # DB에서 등록 데이터 가져오기
    db = DBManager()
    if not db.connect():
        return []
    
    try:
        cursor = db.get_cursor()
        query = "SELECT date, fuel_type, region, cnt FROM cnt_tbl"
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results]
    
    except Exception as e:
        print(f"[REGISTRATION_SERVICE] 전체 데이터 조회 실패 ❌: {e}")
        return []
    finally:
        db.close()

def get_registration_trend():
   # 전년 대비 신규 증가량!!!
    rows = get_registration_count_list()
    if not rows:
        return []
    
    try:
        df = pd.DataFrame(rows)
        # 1. 각 연도별 최신 달(보통 12월) 데이터만 추출 (누적 대수 기준점)
        df['year_val'] = df['date'] // 100
        latest_month_per_year = df.groupby('year_val')['date'].transform('max')
        df_latest = df[df['date'] == latest_month_per_year].copy()
        
        # 2. 연도별, 타입별(전기/내연) 합계
        df_latest['type'] = df_latest['fuel_type'].apply(lambda x: 'electric' if x == '전기' else 'combustion')
        annual_totals = df_latest.groupby(['year_val', 'type'])['cnt'].sum().unstack(fill_value=0)
        
        # 3. 전년 대비 증가량 계산
        # diff()를 사용하여 (올해 누적 - 작년 누적) = 올해 신규 등록량 산출
        annual_diff = annual_totals.diff().dropna()
        
        trend_data = []
        for year, row in annual_diff.iterrows():
            trend_data.append({
                "year": str(int(year)),
                "electric": int(row.get('electric', 0)),
                "combustion": int(row.get('combustion', 0))
            })
            
        return trend_data
    except Exception as e:
        print(f"[REGISTRATION_SERVICE] 증가량 가공 실패 ❌: {e}")
        return []
