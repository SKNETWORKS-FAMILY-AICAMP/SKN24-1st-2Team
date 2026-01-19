from src.feature.fuel.crawl_fuel import get_raw_fuel_data
def transform_fuel_data(raw_data):
    transformed_data = []

    # 1. Diesel 평균
    if raw_data['디젤']:
        avg_diesel = round(sum(raw_data['디젤']) / len(raw_data['디젤']), 2)
        transformed_data.append(('디젤', avg_diesel))

    # 2. LPG 평균 (단위 환산 포함)
    if raw_data['LPG']:
        # kg > L 단위 환산 계수: 0.584
        avg_lpg = round((sum(raw_data['LPG']) / len(raw_data['LPG']) * 0.584), 2)
        transformed_data.append(('LPG', avg_lpg))

    # 3. EV 평균
    if raw_data['전기']:
        avg_ev = round(sum(raw_data['전기']) / len(raw_data['전기']), 2)
        transformed_data.append(('전기', avg_ev))

    # 4. 기타 추가
    transformed_data.append(('기타', 0.0))

    return transformed_data 