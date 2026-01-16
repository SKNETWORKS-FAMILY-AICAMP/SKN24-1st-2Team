from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def cost_fuel():
    # 크롬 드라이버 연결
    path = 'chromedriver.exe'
    service = webdriver.chrome.service.Service(path)
    driver = webdriver.Chrome(service=service)

    # 디젤 가격 크롤링
    # Opinet(주유소 평균판매가격) url 요청
    url = 'https://www.opinet.co.kr/user/dopospdrg/dopOsPdrgAreaView.do'
    driver.get(url)
    time.sleep(1)

    # 가격 리스트 생성
    cost_rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#numbox>tr')

    cost_list = []
    for cost_row in cost_rows:
        cost_tag = cost_row.find_elements(By.CSS_SELECTOR, 'td')[3]
        cost = float(cost_tag.text.replace(',', ''))
        cost_list.append(cost)

    # 평균 값 계산
    avg_disel_cost = round(sum(cost_list) / len(cost_list), 2)

    # LPG 가격 크롤링
    # Opinet(LPG 평균판매가격) url 요청
    url = 'https://www.opinet.co.kr/user/dopcsavsel/dopCsAreaselSelect.do'
    driver.get(url)
    time.sleep(1)

    # 가격 리스트 생성
    cost_rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#numbox>tr')

    cost_list = []
    for cost_row in cost_rows:
        cost_tag = cost_row.find_elements(By.CSS_SELECTOR, 'td')[2]
        cost = float(cost_tag.text.replace(',', ''))
        cost_list.append(cost)

    # 평균 값 계산 / L당 가격으로 치환
    avg_lpg_cost = round((sum(cost_list)/len(cost_list)*0.584), 2)

    # 전기차 가격 크롤링
    # 무공해차 통합누리집(사업자별 전기차 충전 요금) url 요청
    url = 'https://ev.or.kr/nportal/evcarInfo/initEvcarChargePrice.do#'
    driver.get(url)
    time.sleep(1)

    # 표시 행 수 늘리기
    filter_btn = driver.find_element(By.XPATH, '//*[@id="selExcelCnt"]/option[5]')
    filter_btn.click()
    time.sleep(1)

    # 가격 리스트 생성
    cost_rows = driver.find_elements(By.CSS_SELECTOR, 'table.table01>tbody>tr')

    cost_list = []
    for cost_row in cost_rows:
        charger_type = cost_row.find_elements(By.CSS_SELECTOR, 'td')[1].text
        if charger_type == '급속':
            cost = float(cost_row.find_elements(By.CSS_SELECTOR, 'td')[2].text)
            cost_list.append(cost)

    # 평균 값 계산 / L당 가격으로 치환
    avg_ev_cost = round(sum(cost_list)/len(cost_list), 2)

    driver.quit()
    return avg_disel_cost, avg_lpg_cost, avg_ev_cost