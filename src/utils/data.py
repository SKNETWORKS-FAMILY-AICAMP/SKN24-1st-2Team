"""
예시를 위한 더미 데이터 및 데이터 조회(폴백) 함수들을 제공합니다.

- 현재는 `pages/statistics.py`에서 사용하는 **통계/현황 데이터만** 제공합니다.
- TODO: `src/services/`에서 데이터 가공/조회 로직이 구현되면, 이 파일은 제거됩니다.
"""

import importlib
from functools import lru_cache
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
from PIL import Image

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
# 이미지 유틸
# ==============================================================================

_DEFAULT_CAR_IMAGE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="bg" x1="0" x2="1">
      <stop offset="0" stop-color="#0b0d11"/>
      <stop offset="1" stop-color="#111318"/>
    </linearGradient>
  </defs>
  <rect width="800" height="450" rx="18" fill="url(#bg)"/>
  <g fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="6">
    <path d="M140 285c20-55 55-85 110-95l60-10h200l70 20c40 12 65 42 80 85" />
    <path d="M190 285h420" />
  </g>
  <g fill="rgba(255,255,255,0.35)">
    <circle cx="255" cy="300" r="26"/>
    <circle cx="545" cy="300" r="26"/>
  </g>
  <text x="50%" y="56%" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="20" font-family="system-ui, -apple-system, Segoe UI, Roboto">
    이미지 준비 중
  </text>
</svg>
"""


def default_car_image_data_url() -> str:
    """
    이미지가 없거나 로드 실패 시 사용할 기본 SVG(data URL)를 반환합니다.
    """
    return "data:image/svg+xml;utf8," + quote(_DEFAULT_CAR_IMAGE_SVG)


def image_html(image_src, *, alt="", fit="contain"):
    """
    Streamlit `st.markdown(..., unsafe_allow_html=True)`에서 바로 사용할 수 있는 <img> 태그 문자열을 반환합니다.

    - image_src: URL(https://...) 또는 로컬 파일 경로
    """
    src = image_src or default_car_image_data_url()
    # HTML 속성 안전 처리
    src_escaped = escape(str(src), quote=True)
    alt_escaped = escape(alt, quote=True)
    fit_css = escape(fit, quote=True)
    return (
        f'<img src="{src_escaped}" alt="{alt_escaped}" '
        f'style="width:100%;height:100%;object-fit:{fit_css};display:block;" />'
    )


def _is_url(s):
    return s.startswith("http://") or s.startswith("https://")


@lru_cache(maxsize=128)
def fetch_image_bytes(image_ref, *, timeout=8):
    """
    URL/로컬 경로에서 이미지를 bytes로 가져옵니다(간단 캐시 포함).
    """
    if not image_ref:
        return None

    try:
        if _is_url(str(image_ref)):
            resp = requests.get(image_ref, timeout=timeout)
            resp.raise_for_status()
            return resp.content

        p = Path(image_ref)
        if p.exists() and p.is_file():
            return p.read_bytes()
    except Exception:
        return None

    return None


def load_image_pil(image_ref, *, timeout=8):
    """
    URL/로컬 경로에서 이미지를 로드하여 PIL Image로 반환합니다.
    실패 시 기본 SVG를 PIL로 변환할 수 없으므로, 빈 이미지(검정 배경)를 반환합니다.
    """
    if not image_ref:
        # Pillow는 SVG를 직접 열지 못하므로, 안전한 단색 폴백
        return Image.new("RGB", (800, 450), color=(10, 10, 10))

    b = fetch_image_bytes(image_ref, timeout=timeout)
    if not b:
        return Image.new("RGB", (800, 450), color=(10, 10, 10))

    try:
        return Image.open(BytesIO(b)).convert("RGBA")
    except Exception:
        return Image.new("RGB", (800, 450), color=(10, 10, 10))

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

# ==============================================================================
# DB 더미 데이터 (schema.py 테이블 구조 기반)
# ==============================================================================

def get_dummy_fuel_data():
    """
    fuel_tbl 더미 데이터
    컬럼: fuel_type, fuel_cost
    """
    return [
        ("전기", 150.00),
        ("수소", 6500.00),
        ("경유", 1450.00),
        ("LPG", 900.00),
        ("가솔린", 1650.00),
    ]


def get_dummy_region_data():
    """
    region_tbl 더미 데이터
    컬럼: region, charger_cnt
    """
    return [
        ("서울", 4250),
        ("경기", 5820),
        ("인천", 1120),
        ("강원", 1540),
        ("충청", 2180),
        ("전라", 2420),
        ("경상", 3650),
        ("제주", 890),
    ]


def get_dummy_cnt_data():
    """
    cnt_tbl 더미 데이터
    컬럼: fuel_type, region, date, cnt
    date 형식: YYYYMM (예: 202501)
    """
    regions = ["서울", "경기", "인천", "강원", "충청", "전라", "경상", "제주"]
    fuel_types = ["전기", "수소", "경유", "LPG", "가솔린"]
    dates = [202301, 202302, 202303, 202401, 202402, 202403, 202501]
    
    data = []
    for date in dates:
        for region in regions:
            for fuel_type in fuel_types:
                # 더미 등록 대수 생성 (지역과 연료 유형별로 다른 값)
                base = hash(f"{region}{fuel_type}{date}") % 10000
                cnt = abs(base) + 100  # 최소 100대
                data.append((fuel_type, region, date, cnt))
    
    return data


def get_dummy_car_info_data():
    """
    car_info_tbl 더미 데이터
    컬럼: fuel_type, name, maker, size, capacity, h_power, max_fuel, 
          cx_efc, ct_efc, hw_efc, max_dist, price, image
    """
    return [
        # 전기 차량
        ("전기", "e-마스터", "현대", "대형", 3.5, 300, 64.0, None, None, None, 400, 85000000, "https://autoimg.danawa.com/photo/4404/model_360.png"),
        ("전기", "포터2 전기", "기아", "소형", 1.0, 100, 35.0, None, None, None, 200, 45000000, "https://autoimg.danawa.com/photo/4404/model_360.png"),
        ("전기", "봉고3 전기", "기아", "중형", 1.5, 140, 58.0, None, None, None, 350, 65000000, "https://autoimg.danawa.com/photo/4404/model_360.png"),
        ("전기", "라보전기", "GM대우", "중형", 1.5, 120, 50.0, None, None, None, 300, 58000000, "https://autoimg.danawa.com/photo/4404/model_360.png"),
    ]


def get_dummy_faq_category_data():
    """
    faq_category_tbl 더미 데이터
    컬럼: category_code, category_name
    """
    return [
        (1, "구매/보조금"),
        (2, "충전/운행"),
        (3, "정비/보험"),
        (4, "환경/정책"),
        (5, "기타"),
    ]


def get_dummy_faq_data():
    """
    faq_tbl 더미 데이터
    컬럼: category_code, category_name, question, answer, source_url, related_car_type
    """
    return [
        # 카테고리 1: 구매/보조금
        (1, "구매/보조금", "전기 화물차 구매 시 보조금은 얼마나 받을 수 있나요?", "전기 화물차는 구매가의 최대 40%까지 보조금을 받을 수 있으며, 지역에 따라 차이가 있습니다.", "https://www.ev.or.kr", "전기"),
        (1, "구매/보조금", "수소 화물차 보조금 신청 방법은?", "환경부 누리집에서 신청 가능하며, 차량 등록 후 3개월 이내 신청해야 합니다.", "https://www.me.go.kr", "수소"),
        
        # 카테고리 2: 충전/운행
        (2, "충전/운행", "전기 화물차 충전 시간은 얼마나 걸리나요?", "급속 충전 시 30분~1시간, 완속 충전 시 6~8시간 소요됩니다.", "https://www.ev.or.kr", "전기"),
        (2, "충전/운행", "수소 충전소는 어디에 있나요?", "전국 주요 고속도로와 도심에 위치하며, 실시간 위치는 수소충전소 앱에서 확인 가능합니다.", "https://www.h2korea.or.kr", "수소"),
        (2, "충전/운행", "경유 화물차 연비 향상 방법은?", "적정 속도 유지, 정기 정비, 공회전 최소화로 연비를 개선할 수 있습니다.", "https://www.energy.or.kr", "경유"),
        
        # 카테고리 3: 정비/보험
        (3, "정비/보험", "전기 화물차 정비 비용은 얼마나 드나요?", "내연기관 대비 정비 부품이 적어 전반적으로 정비비용이 30~40% 저렴합니다.", "https://www.insurance.or.kr", "전기"),
        (3, "정비/보험", "화물차 종합보험료 계산 기준은?", "차량 종류, 용도, 운전자 연령 등에 따라 보험료가 달라집니다.", "https://www.insurance.or.kr", "전기"),
        
        # 카테고리 4: 환경/정책
        (4, "환경/정책", "배출가스 규제 대응을 위한 차량 선택은?", "2025년부터 강화되는 배출가스 규제를 고려하면 전기·수소 차량이 유리합니다.", "https://www.me.go.kr", "전기"),
        (4, "환경/정책", "탄소중립 로드맵에 따른 화물차 정책 변화는?", "2030년까지 전기·수소 차량 비중을 30%로 확대하는 계산 기준은?", "https://www.me.go.kr", "전기"),
        
        # 카테고리 5: 기타
        (5, "기타", "화물차 중고 매매 시 주의사항은?", "차량 등록증, 정비 이력, 사고 이력을 꼼꼼히 확인하는 것이 중요합니다.", "https://www.usedcar.go.kr", "전기"),
    ]

def get_all_dummy_data():
    """
    모든 더미 데이터를 딕셔너리로 반환
    
    Returns:
        dict: 테이블명을 키로 하는 더미 데이터 딕셔너리
    """
    return {
        "fuel_tbl": get_dummy_fuel_data(),
        "region_tbl": get_dummy_region_data(),
        "cnt_tbl": get_dummy_cnt_data(),
        "car_info_tbl": get_dummy_car_info_data(),
        "faq_category_tbl": get_dummy_faq_category_data(),
        "faq_tbl": get_dummy_faq_data(),
    }