def transform_region_data(regions, counts):
    """수집된 데이터를 정수형으로 변환하고 튜플 리스트로 구성"""
    transformed_data = []
    
    for region, count in zip(regions, counts):
        # 쉼표 제거 후 정수 변환
        clean_count = int(count.replace(',', ''))
        transformed_data.append((region, clean_count))
        
    return transformed_data # [('서울', 500), ('부산', 300), ...]