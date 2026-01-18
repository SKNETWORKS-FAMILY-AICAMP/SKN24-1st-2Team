from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os, time


# 경로 설정
url = 'https://stat.molit.go.kr/portal/cate/statMetaView.do?hRsId=58'
rel_path = '../../../data/raw/registered_cars'
abs_path = os.path.abspath(rel_path)


options = Options()
# 다운로드 경로 설정
options.add_experimental_option("prefs", {
    "download.default_directory": abs_path,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

# 크롬 실행, 통계사이트 접속
service = Service()
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
time.sleep(1)

# 엑셀 모음 박스
excels = driver.find_elements(By.CSS_SELECTOR, ".file-sch-list > li > a")

# 9월, 8월, ..., 1월, 12월, 11월, 10월 순으로 받는 찐빠가 있긴 함
# 근데 적절한 년도에서 for문을 끊기 위한 정렬이므로 사소함.
sorted_xls = sorted(excels, key=lambda x: x.text, reverse=True)

# 한 박스에 다운버튼이 2개라 중복되는 경우가 있음
dwnld_files = []

cnt = 1
for xl in sorted_xls:
    if "2015년" in xl.text:
        break

    if ("자동차 등록" in xl.text) and (xl.text not in dwnld_files):
        print(cnt, ":", xl.text)
        dwnld_files.append(xl.text)
        driver.execute_script("arguments[0].click()", xl)
        cnt += 1
        time.sleep(0.5) # 너무 빠르게 받으면 몇개 놓침
        

time.sleep(2)
print("종료")


