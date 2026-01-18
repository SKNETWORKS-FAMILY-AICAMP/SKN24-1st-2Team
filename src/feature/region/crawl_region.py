from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def get_raw_region_data():
    """차지인포 사이트에서 지역명과 충전소 개수 리스트 수집"""
    service = Service()
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = 'https://chargeinfo.ksga.org/front/statistics/charger'
        driver.get(url)
        time.sleep(1)
        
        # 1. 지역 이름 수집
        region_row = driver.find_elements(By.CSS_SELECTOR, 'table.datatable>thead>tr>th')
        regions = [r.text for r in region_row[1:]]
        if regions:
            regions[-1] = '전국' # 마지막 항목 보정
        
        # 2. 충전소 개수 수집
        first_row = driver.find_element(By.CSS_SELECTOR, 'tbody#tBodyList>tr')
        cells = first_row.find_elements(By.CSS_SELECTOR, 'td')
        counts = [c.text.split('\n')[0] for c in cells[1:]]
        
        return regions, counts

    finally:
        driver.quit()