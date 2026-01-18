import pandas as pd
import os

rel_raw_path = '../../../data/raw/registered_cars'
abs_raw_path = os.path.abspath(rel_raw_path)

# 경로에서 엑셀 파일들 긁어오기
all_files = os.listdir(abs_raw_path)
xl_names = [f for f in all_files if f.endswith('.xlsx')]
xl_files = [os.path.join(abs_raw_path, f) for f in xl_names]

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
    
    # fuel_type: 연료별, type: 종별(승용/화물/...), usage: 용도별(비사업용/사업용/계)
    df.rename(columns={df.columns[0]: 'fuel_type', df.columns[1]: 'type', df.columns[2]: 'usage'}, inplace=True)
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

# 내연, 전기, 기타로 통일
fuel_map = {
    '휘발유': '내연', '경유': '내연', '엘피지': '내연', 'CNG': '내연', '등유': '내연', 'LNG': '내연',
    '전기': '전기',
    '수소': '기타', '수소전기': '기타', '하이브리드(휘발유+전기)': '기타', 
    '하이브리드(경유+전기)': '기타', '하이브리드(LPG+전기)': '기타', '기타연료': '기타'
}
result_df['fuel_type'] = result_df['fuel_type'].map(fuel_map)

# 3개로 줄어든 fuel_type에 따라 공통된 값을 하나로 합침
result_df = result_df.groupby(['date', 'region', 'fuel_type'])['cnt'].sum().reset_index()


print("\nProcess complete")
print("\n\n")

# CSV 파일로 저장
rel_output_path = '../../../data/processed/registered_cars'
# abs_output_path = os.path.abspath(rel_output_path)
os.makedirs(rel_output_path, exist_ok=True)
output = os.path.join(rel_output_path, 'processed_registered_cars.csv')
result_df.to_csv(output, index=False, encoding='utf-8-sig')
print(f"Data saved: {rel_output_path}")


    


