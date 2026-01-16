from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def crawling():
    # 크롬 드라이버 연결
    path = 'chromedriver.exe'
    service = webdriver.chrome.service.Service(path)
    driver = webdriver.Chrome(service=service)
    
    # 차지인포 url 요청
    url = 'https://chargeinfo.ksga.org/front/statistics/charger'
    driver.get(url)
    time.sleep(1)
    
    # region_list 생성
    region_row = driver.find_elements(By.CSS_SELECTOR, 'table.datatable>thead>tr>th')
    
    region_list = []
    for region in region_row[1:]:
        region_list.append(region.text)

    region_list[-1] = '전국'
    
    # charger_cnt_list 생성
    first_charger_row = driver.find_element(By.CSS_SELECTOR, 'tbody#tBodyList>tr')
    charger_cnt_cells = first_charger_row.find_elements(By.CSS_SELECTOR, 'td')
    
    charger_cnt_list = []
    for charger_cnt_cell in charger_cnt_cells[1:]:
        charger_cnt = charger_cnt_cell.text.split('\n')[0]
        # 정수형으로 변경
        charger_cnt = int(charger_cnt.replace(',', ''))
        charger_cnt_list.append(charger_cnt)
    
    driver.quit()

    return region_list, charger_cnt_list

