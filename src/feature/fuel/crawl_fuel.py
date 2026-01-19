from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def get_raw_fuel_data():
    """Opinet 및 무공해차 사이트에서 연료별 가격 리스트 수집"""
    service = Service()
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)

    data = {
        '디젤': [],
        'LPG': [],
        '전기': []
    }

    try:
        # 1. 디젤 가격 수집
        driver.get('https://www.opinet.co.kr/user/dopospdrg/dopOsPdrgAreaView.do')
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#numbox>tr')
        data['디젤'] = [float(r.find_elements(By.CSS_SELECTOR, 'td')[3].text.replace(',', '')) for r in rows]

        # 2. LPG 가격 수집
        driver.get('https://www.opinet.co.kr/user/dopcsavsel/dopCsAreaselSelect.do')
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, 'tbody#numbox>tr')
        data['LPG'] = [float(r.find_elements(By.CSS_SELECTOR, 'td')[2].text.replace(',', '')) for r in rows]

        # 3. 전기차 가격 수집
        driver.get('https://ev.or.kr/nportal/evcarInfo/initEvcarChargePrice.do#')
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="selExcelCnt"]/option[5]').click() # 100개씩 보기
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, 'table.table01>tbody>tr')
        for r in rows:
            cols = r.find_elements(By.CSS_SELECTOR, 'td')
            if cols[1].text == '급속':
                data['전기'].append(float(cols[2].text))

    finally:
        driver.quit()
    
    return data