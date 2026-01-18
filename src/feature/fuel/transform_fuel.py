from src.fuel.crawl_fuel import get_raw_fuel_data
def transform_fuel_data(raw_data):
    transformed_data = []

    # 1. Diesel 평균
    if raw_data['Diesel']:
        avg_diesel = round(sum(raw_data['Diesel']) / len(raw_data['Diesel']), 2)
        transformed_data.append(('Diesel', avg_diesel))

    # 2. LPG 평균 (단위 환산 포함)
    if raw_data['LPG']:
        # kg > L 단위 환산 계수: 0.584
        avg_lpg = round((sum(raw_data['LPG']) / len(raw_data['LPG']) * 0.584), 2)
        transformed_data.append(('LPG', avg_lpg))

    # 3. EV 평균
    if raw_data['EV']:
        avg_ev = round(sum(raw_data['EV']) / len(raw_data['EV']), 2)
        transformed_data.append(('EV', avg_ev))

    return transformed_data 