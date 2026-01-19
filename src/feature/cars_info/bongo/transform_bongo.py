"""
봉고 차량 정보 데이터 변환 모듈
bongo.json을 DB 스키마에 맞게 변환
"""
import json
import re
from pathlib import Path


def parse_number(value: str) -> float:
    """문자열에서 숫자만 추출하여 float로 변환"""
    if not value:
        return 0.0
    # 쉼표와 단위 제거 후 숫자만 추출
    numbers = re.findall(r'[\d.]+', value.replace(',', ''))
    return float(numbers[0]) if numbers else 0.0


def parse_integer(value: str) -> int:
    """문자열에서 숫자만 추출하여 int로 변환"""
    if not value:
        return 0
    # 쉼표와 단위 제거 후 숫자만 추출
    numbers = re.findall(r'\d+', value.replace(',', ''))
    return int(numbers[0]) if numbers else 0


def extract_horsepower(power_str: str) -> int:
    """최고출력 문자열에서 마력 추출 (예: "138/3,800 ps/rpm" -> 138)"""
    if not power_str:
        return 0
    # 첫 번째 숫자 추출
    match = re.search(r'(\d+)', power_str)
    return int(match.group(1)) if match else 0


def normalize_fuel_type(fuel_str: str) -> str:
    """연료 타입 정규화"""
    if not fuel_str:
        return "기타"
    if "전기" in fuel_str or "배터리" in fuel_str:
        return "전기"
    elif "LPG" in fuel_str:
        return "LPG"
    elif "디젤" in fuel_str:
        return "디젤"
    elif "가솔린" in fuel_str:
        return "가솔린"
    else:
        return "기타"


def extract_fuel_capacity(specs: dict, fuel_type: str) -> float:
    """연료 용량 추출 (LPG는 연료탱크, 전기는 배터리 용량)"""
    if fuel_type == "전기":
        battery = specs.get("배터리 용량", "")
        if battery:
            # "60.4 kWh" -> 60.4
            return parse_number(battery)
    else:
        fuel_tank = specs.get("연료탱크", "")
        if fuel_tank:
            # "75 ℓ" -> 75.0
            return parse_number(fuel_tank)
    return 0.0


def extract_fuel_efficiency(specs: dict, fuel_type: str, efficiency_type: str) -> float:
    """연비 추출 (LPG는 km/ℓ, 전기는 km/kWh)"""
    if fuel_type == "전기":
        key_map = {
            "복합": "복합전비",
            "도심": "도심전비",
            "고속": "고속전비"
        }
    else:
        key_map = {
            "복합": "복합연비",
            "도심": "도심연비",
            "고속": "고속연비"
        }
    
    key = key_map.get(efficiency_type, "")
    if key and key in specs:
        value = specs[key]
        # "7.0 km/ℓ" 또는 "3.1 km/kWh" -> 7.0 또는 3.1
        return parse_number(value)
    return 0.0


def extract_max_distance(specs: dict, fuel_type: str, max_fuel: float = 0, cx_efc: float = 0) -> int:
    """최대 주행거리 추출
    
    - 전기차: 복합 주행거리 스펙에서 추출
    - LPG 등: 연료탱크 용량 × 복합연비로 계산
    """
    if fuel_type == "전기":
        distance = specs.get("복합 주행거리", "")
        if distance:
            # "217 km" -> 217
            return parse_integer(distance)
    else:
        # LPG 등: 연료탱크 용량 × 복합연비
        if max_fuel > 0 and cx_efc > 0:
            return int(max_fuel * cx_efc)
    return 0


def transform_bongo_data(raw_data_path: Path = None):

    if raw_data_path is None:
        # json 저장 경로
        raw_data_path = Path(__file__).parents[4] / "data" / "raw" / "car_info" / "bongo.json"
    
    # JSON 파일 읽기
    with open(raw_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    transformed_data = []
    
    # 각 모델별로 처리
    for model_key, model_data in raw_data.items():
        model_name = model_data.get("model", "")
        model_image_url = model_data.get("image_url", "")
        maker = "기아"  # 봉고는 기아 제품
        
        # 모델명 또는 모델 키에 "EV"가 포함되어 있으면 전기로 설정
        is_ev_model = "EV" in model_key.upper() or "EV" in model_name.upper()
        
        # 각 라인업별로 처리
        for lineup in model_data.get("lineup", []):
            trims = lineup.get("trims", {})
            specs = lineup.get("specs", {})
            
            # 필수 정보 확인
            if not trims.get("name") or not specs:
                continue
            
            # 연료 타입: 모델명에 EV가 있으면 전기, 아니면 specs에서 추출
            if is_ev_model:
                fuel_type = "전기"
            else:
                fuel_type = normalize_fuel_type(specs.get("연료", ""))
            
            # LPG와 전기만 저장
            if fuel_type not in ["LPG", "전기"]:
                continue
            
            # 차량 모델명 (세부모델명)
            name = trims.get("name", "").strip()
            if not name:
                continue
            
            # 적재량
            capacity_str = specs.get("적재량", "")
            capacity = parse_number(capacity_str) if capacity_str else 0.0
            
            # 최고출력 (마력)
            power_str = specs.get("최고출력", "") or specs.get("모터 최고출력", "")
            h_power = extract_horsepower(power_str)
            
            # 연료 용량
            max_fuel = extract_fuel_capacity(specs, fuel_type)
            
            # 연비
            cx_efc = extract_fuel_efficiency(specs, fuel_type, "복합")
            ct_efc = extract_fuel_efficiency(specs, fuel_type, "도심")
            hw_efc = extract_fuel_efficiency(specs, fuel_type, "고속")
            
            # 최대 주행거리 (LPG는 연료탱크 × 복합연비로 계산)
            max_dist = extract_max_distance(specs, fuel_type, max_fuel, cx_efc)
            
            # 가격
            price_str = trims.get("price", "")
            price = parse_integer(price_str) if price_str else 0
            
            # 유지비 추출 (specs에서 "유지비용" 또는 "유지비" 필드 확인)
            maintenance_cost = None
            maintenance_str = specs.get("유지비용", "") or specs.get("유지비", "")
            if maintenance_str:
                # "6,490,740" 형식에서 숫자만 추출하여 만원 단위로 변환
                maintenance_num = parse_integer(maintenance_str)
                if maintenance_num > 0:
                    # 원 단위를 만원 단위로 변환
                    maintenance_cost = maintenance_num // 10000
            
            # 변환된 데이터 추가
            transformed_data.append({
                "fuel_type": fuel_type,
                "name": name,
                "maker": maker,
                "size": "소형",  # 1톤 화물차는 소형
                "capacity": capacity,
                "h_power": h_power,
                "max_fuel": max_fuel,
                "cx_efc": cx_efc if cx_efc > 0 else None,
                "ct_efc": ct_efc if ct_efc > 0 else None,
                "hw_efc": hw_efc if hw_efc > 0 else None,
                "max_dist": max_dist,
                "price": price,
                "maintenance_cost": maintenance_cost,
                "image": model_image_url if model_image_url else None
            })
    
    return transformed_data


if __name__ == "__main__":
    # 테스트 실행
    data = transform_bongo_data()
    print(f"변환된 데이터 수: {len(data)}")
    if data:
        print("\n첫 번째 데이터 예시:")
        import json
        print(json.dumps(data[0], ensure_ascii=False, indent=2))
