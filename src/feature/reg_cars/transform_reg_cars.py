import pandas as pd
import os

data_path = 'data/raw/registered_cars' # 프로젝트 루트 기준 상대 경로

# 경로에서 엑셀 파일들 긁어오기
all_files = os.listdir(data_path)
xl_names = [f for f in all_files if f.endswith('.xlsx')]
xl_files = [os.path.join(data_path, f) for f in xl_names]

# for xl in xl_files:
#     print(xl)


all_processed_df = []

print("Starting processing")

# 각 엑셀 파일 순회
for file_path in xl_files:
    file_name = os.path.basename(file_path) # 이름 빼기
    print(f"Processing: {file_name}")

    # date값 저장 (년, 월) => date_key
    base_name = os.path.splitext(file_name)[0]
    year = base_name.split('년_')[0]
    month = base_name.split('년_')[1].split('월')[0]
    if len(month) != 2:
        month = '0' + month
    
    date_key = f"{year}{month}"
    

    xls = pd.ExcelFile(file_path)
    # 파일 내 시트명 순회
    for sheet_name in xls.sheet_names:
        if '연료별' in sheet_name:
            target_sheet_name = sheet_name
            break
    
    if not target_sheet_name:
        print("!!! 타겟 시트를 찾지 못함 !!!")
        continue


    region_header_idx = 2
    df = pd.read_excel(xls, sheet_name=target_sheet_name, header=region_header_idx)

    # 1. 필수 컬럼명 변경
    df.rename(columns={df.columns[0]: 'fuel_type', df.columns[1]: 'type', df.columns[2]: 'usage'}, inplace=True)

    # 2. 필요한 지역 컬럼만 명시적으로 선택 (가장 안정적인 방법)
    # 이렇게 하면 '계'나 다른 불필요한 컬럼이 있어도 무시됨
    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    columns_to_keep = ['fuel_type', 'type', 'usage'] + regions
    df = df[columns_to_keep]

    # 3. 이후 로직 진행
    df['fuel_type'] = df['fuel_type'].ffill()
    df['type'] = df['type'].ffill()

    df_filtered = df[(df['type'] == '화물') & (df['usage'] == '계')].copy()
    # print(df_filtered)

    id_vars = ['fuel_type']
    value_vars = [col for col in df_filtered.columns if col not in ['fuel_type', 'type', 'usage']]
    df_melted = df_filtered.melt(id_vars=id_vars, value_vars=value_vars, var_name='region', value_name='cnt')
    df_melted['date'] = date_key
    # print(df_melted)

    # '계'가 작성된 부분 삭제.
    df_melted = df_melted[~df_melted['fuel_type'].astype(str).str.contains('계')]
    df_melted = df_melted[~df_melted['region'].astype(str).str.contains('계')]
    # print(df_melted)
    processed_df = df_melted[['date', 'region', 'fuel_type', 'cnt']]
    all_processed_df.append(processed_df)

# 각 df를 전부 concat, 데이터 타입 통일
result_df = pd.concat(all_processed_df, ignore_index=True)
result_df['date'] = pd.to_numeric(result_df['date'])
result_df['cnt'] = pd.to_numeric(result_df['cnt'])

# 지역 8도 기준으로 통일
region_map = {
    '서울': '서울', '인천': '인천', '경기': '경기', '강원': '강원', '제주': '제주',
    '충북': '충청', '충남': '충청', '대전': '충청', '세종': '충청',
    '전북': '전라', '전남': '전라', '광주': '전라',
    '경북': '경상', '경남': '경상', '부산': '경상', '대구': '경상', '울산': '경상'
}
result_df['region'] = result_df['region'].map(region_map)

# 8도로 줄어든 region에 따라 공통된 값을 하나로 합침
result_df = result_df.groupby(['date', 'region', 'fuel_type'])['cnt'].sum().reset_index()


# 4가지 연료(디젤, LPG, 전기, 기타) 기준으로 통일
fuel_map = {
    '경유': '디젤',
    '엘피지': 'LPG',
    '전기': '전기',
    # --- 아래는 모두 '기타'로 통합 ---
    '휘발유': '기타',
    'CNG': '기타',
    '등유': '기타',
    'LNG': '기타',
    '수소': '기타',
    '수소전기': '기타',
    '하이브리드(휘발유+전기)': '기타',
    '하이브리드(경유+전기)': '기타',
    '하이브리드(LPG+전기)': '기타',
    '하이브리드(CNG+전기)': '기타',
    '하이브리드(LNG+전기)': '기타',
    '기타연료': '기타',
    '알코올': '기타',
    '태양열': '기타'
}
result_df['fuel_type'] = result_df['fuel_type'].map(fuel_map)

# 4개로 줄어든 fuel_type에 따라 공통된 값을 하나로 합침
result_df = result_df.groupby(['date', 'region', 'fuel_type'])['cnt'].sum().reset_index()

print("\nProcess complete")
print("\n\n")

# CSV 파일로 저장
output_dir = 'data/processed/registered_cars' # 프로젝트 루트 기준 상대 경로
os.makedirs(output_dir, exist_ok=True)
output_file_path = os.path.join(output_dir, 'processed_registered_cars.csv')
result_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
print(f"Data saved: {output_file_path}")


    


