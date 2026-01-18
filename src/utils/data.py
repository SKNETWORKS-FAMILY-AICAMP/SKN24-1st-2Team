"""
예시를 위한 더미 데이터 및 데이터 조회(폴백) 함수들을 제공합니다.

- 현재는 `pages/statistics.py`에서 사용하는 **통계/현황 데이터만** 제공합니다.
- TODO: `src/services/`에서 데이터 가공/조회 로직이 구현되면, 이 파일은 제거됩니다.
"""

import importlib
import pandas as pd

from config import LOCATION_COORDS

def _optional_service_fn(module_path, fn_name):
    """
    서비스 레이어 함수가 있으면 가져오고, 없으면 None을 반환합니다.
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, fn_name, None)
    except Exception:
        return None


# 서비스 레이어 조회 함수들(있으면 사용, 없으면 더미 데이터로 폴백)
get_region_list = _optional_service_fn("src.services.region_service", "get_region_list")
get_registration_count_list = _optional_service_fn(
    "src.services.registration_service", "get_registration_count_list"
)

# ==============================================================================
# 통계/현황(지도) 데이터
# ==============================================================================

def get_paldo_charging_data():
    """
    팔도(권역)별 충전소 개수 DataFrame
    컬럼: region, count, lat, lon
    """
    regions = ["서울", "경기", "인천", "강원", "충청", "전라", "경상", "제주"]

    # 서비스 레이어가 준비되면 DB에서 조회하고, 아니면 더미로 폴백
    if get_region_list:
        try:
            db_rows = get_region_list()  # 예: [{"region": "서울", "charger_cnt": 4250}, ...]
            charger_by_region = {r["region"]: r["charger_cnt"] for r in db_rows}
            counts = [int(charger_by_region.get(r, 0)) for r in regions]
        except Exception:
            counts = [4250, 5820, 1120, 1540, 2180, 2420, 3650, 890]
    else:
        counts = [4250, 5820, 1120, 1540, 2180, 2420, 3650, 890]

    data = {
        "region": regions,
        "count": counts,
        # LOCATION_COORDS: (lon, lat)
        "lat": [LOCATION_COORDS[r][1] for r in regions],
        "lon": [LOCATION_COORDS[r][0] for r in regions],
    }
    return pd.DataFrame(data)


def get_paldo_ratio_data():
    """
    팔도(권역)별 전기 화물차 비중(%) DataFrame
    컬럼: region, count(비중), lat, lon
    """
    regions = ["서울", "경기", "인천", "강원", "충청", "전라", "경상", "제주"]

    # 서비스 레이어가 준비되면 최신 월 기준으로 비중을 계산하고, 아니면 더미로 폴백
    if get_registration_count_list:
        try:
            # 예: [{"date": 202501, "fuel_type": "전기", "region": "서울", "cnt": 123}, ...]
            rows = get_registration_count_list()
            df = pd.DataFrame(rows)
            if not df.empty and {"date", "fuel_type", "region", "cnt"}.issubset(df.columns):
                latest = int(df["date"].max())
                latest_df = df[df["date"] == latest].copy()

                # 지역별 전체/전기 등록대수 집계
                total_by_region = latest_df.groupby("region")["cnt"].sum()
                electric_by_region = latest_df[latest_df["fuel_type"] == "전기"].groupby("region")["cnt"].sum()

                # 비중(%) 계산
                ratios = []
                for r in regions:
                    total = float(total_by_region.get(r, 0))
                    elec = float(electric_by_region.get(r, 0))
                    ratio = (elec / total * 100.0) if total > 0 else 0.0
                    ratios.append(round(ratio, 1))
                counts = ratios
            else:
                counts = [8.2, 6.5, 7.8, 3.1, 4.8, 4.1, 5.2, 12.5]
        except Exception:
            counts = [8.2, 6.5, 7.8, 3.1, 4.8, 4.1, 5.2, 12.5]
    else:
        counts = [8.2, 6.5, 7.8, 3.1, 4.8, 4.1, 5.2, 12.5]

    data = {
        "region": regions,
        "count": counts,
        # LOCATION_COORDS: (lon, lat)
        "lat": [LOCATION_COORDS[r][1] for r in regions],
        "lon": [LOCATION_COORDS[r][0] for r in regions],
    }
    return pd.DataFrame(data)

# ==============================================================================
# 통계/현황(차트) 데이터
# ==============================================================================

REGISTRATION_TREND_DATA = [
    {"year": "2019", "electric": 1200, "combustion": 45000},
    {"year": "2020", "electric": 2800, "combustion": 43500},
    {"year": "2021", "electric": 5400, "combustion": 41200},
    {"year": "2022", "electric": 9800, "combustion": 38900},
    {"year": "2023", "electric": 18500, "combustion": 35100},
    {"year": "2024", "electric": 32000, "combustion": 31500},
]

MAINTENANCE_COST_DATA = [
    {"category": "연료/충전", "electric": 180, "combustion": 720},
    {"category": "정비", "electric": 45, "combustion": 180},
    {"category": "세금/보험", "electric": 60, "combustion": 95},
    {"category": "기타", "electric": 30, "combustion": 45},
]
