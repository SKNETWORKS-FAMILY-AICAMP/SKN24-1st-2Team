import json
import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from config import BONGO_MODELS


# 모델 정보
OUTPUT_PATH = Path(__file__).parents[4] / "data" / "raw" / "car_info" / "bongo.json"


def setup_logger():
    """로거 설정"""
    logger = logging.getLogger("bongo_crawler")
    logger.setLevel(logging.INFO)
    
    # 핸들러가 이미 있으면 추가하지 않음
    if logger.handlers:
        return logger
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger


# 전역 로거 인스턴스
logger = setup_logger()


def create_driver():
    logger.info("크롬 드라이버 생성 중...")
    options = Options()
    # 페이지 로드 전략은 기본값 사용 (동적 요소 로드를 위해)
    
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(30)
    # implicit wait 제거 - 명시적 sleep으로 처리
    driver.implicitly_wait(0)
    logger.info("크롬 드라이버 생성 완료")
    return driver


def parse_features(features_text):
    result = {}
    if not features_text:
        return result

    # • 카테고리 : 내용 형태로 파싱
    pattern = r'•\s*([^:：]+)\s*[:：]\s*([^•]+)'
    matches = re.findall(pattern, features_text)

    for category, content in matches:
        category = category.strip()
        content = content.strip()
        result[category] = content

    return result


def extract_trim_info_from_price_tab(driver, model_id, lineup_id):
    """가격·제원·사양 탭에서 세부모델명과 가격 추출"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Lineup={lineup_id}&Tab=price"
    logger.debug(f"가격·제원·사양 페이지 접속 중: {url}")
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"페이지 로드 중 오류 발생 (계속 진행): {e}")
    # JavaScript 렌더링 완료를 위한 명시적 대기
    time.sleep(3)
    logger.debug("페이지 로드 완료")

    result = {"name": "", "price": ""}

    # specTable 테이블 찾기
    tables = driver.find_elements(By.CSS_SELECTOR, "table.specTable")
    if not tables:
        logger.warning(f"모델 ID {model_id}, 라인업 ID {lineup_id}: specTable을 찾을 수 없습니다")
        return result
    
    logger.debug(f"specTable 발견: {len(tables)}개")

    table = tables[0]

    # 첫 번째 트림 정보 추출 (해당 라인업의 첫 번째 세부모델)
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    if rows:
        first_row = rows[0]

        # 세부모델명 (tdTitle 클래스)
        trim_els = first_row.find_elements(By.CSS_SELECTOR, "td.tdTitle")
        if trim_els:
            trim_name = trim_els[0].text.replace("\n", " ").strip()
            result["name"] = trim_name
            logger.debug(f"세부모델명 추출: {trim_name}")

        # 가격 (priceInfo 클래스 내부의 num.base)
        price_els = first_row.find_elements(By.CSS_SELECTOR, ".priceInfo .num.base")
        if price_els:
            price_text = price_els[0].text.strip()
            # 숫자와 쉼표만 추출
            price_match = re.search(r'([\d,]+)', price_text)
            if price_match:
                price = price_match.group(1).replace(",", "")
                result["price"] = price
                logger.debug(f"가격 추출: {price}")
        else:
            # 대체 방법: priceInfo 클래스 내부의 모든 텍스트에서 가격 찾기
            price_info_els = first_row.find_elements(By.CSS_SELECTOR, ".priceInfo")
            if price_info_els:
                price_text = price_info_els[0].text.strip()
                price_match = re.search(r'([\d,]+)', price_text)
                if price_match:
                    price = price_match.group(1).replace(",", "")
                    result["price"] = price
                    logger.debug(f"가격 추출 (대체 방법): {price}")

    return result


def extract_spec_detail(driver, model_id, lineup_id):
    """제원·사양/옵션 탭에서 상세 제원 추출"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Lineup={lineup_id}&Tab=spec"
    logger.debug(f"제원 상세 페이지 접속 중: {url}")
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"제원 상세 페이지 로드 중 오류 발생 (계속 진행): {e}")
    # JavaScript 렌더링 완료를 위한 명시적 대기
    time.sleep(3)
    logger.debug("제원 상세 페이지 로드 완료")

    data = {"specs": {}, "trims": {"name": "", "price": ""}}
    
    # 테이블 헤더에서 트림명과 가격 추출 (<span class="trim">, <span class="price">)
    try:
        # compare_table, compare_header, compare__table compare__header 테이블의 thead/tbody에서 추출
        # 먼저 compare__table compare__header 테이블 시도 (더 정확한 트림명)
        header_tables = driver.find_elements(By.CSS_SELECTOR, "table.compare__table.compare__header, table.compare_table thead, table.compare_header thead, table thead")
        
        for table in header_tables:
            # tbody 또는 thead에서 찾기
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr, thead tr")
            for row in rows:
                ths = row.find_elements(By.TAG_NAME, "th")
                # 첫 번째 th는 "항목" 등이므로 제외하고, 나머지 th들이 트림 정보
                for th in ths[1:] if len(ths) > 1 else ths:
                    # <span class="trim">에서 트림명 추출
                    trim_els = th.find_elements(By.CSS_SELECTOR, "span.trim")
                    if trim_els:
                        trim_name = trim_els[0].text.strip()
                        if trim_name and not data["trims"]["name"]:
                            data["trims"]["name"] = trim_name
                            logger.debug(f"트림명 추출: {trim_name}")
                    
                    # <span class="price">에서 가격 추출
                    price_els = th.find_elements(By.CSS_SELECTOR, "span.price")
                    if price_els:
                        price_text = price_els[0].text.strip()
                        # 숫자와 쉼표만 추출 (예: "63,120,000원" -> "63120000")
                        price_match = re.search(r'([\d,]+)', price_text)
                        if price_match:
                            price = price_match.group(1).replace(",", "")
                            if price and not data["trims"]["price"]:
                                data["trims"]["price"] = price
                                logger.debug(f"가격 추출: {price}")
                    
                    # 첫 번째 트림 정보만 사용하므로 찾으면 중단
                    if data["trims"]["name"] and data["trims"]["price"]:
                        break
                if data["trims"]["name"] and data["trims"]["price"]:
                    break
            if data["trims"]["name"] and data["trims"]["price"]:
                break
        
        if not data["trims"]["name"] and not data["trims"]["price"]:
            logger.debug("테이블 헤더에서 트림 정보를 찾을 수 없습니다")
    except Exception as e:
        logger.debug(f"트림 정보 추출 중 오류 발생: {e}")

    # 왼쪽 테이블(항목명)과 오른쪽 테이블(값)을 ID로 매칭하여 추출
    # compareLeft_* (항목명) -> compareRight_* (값들, 첫 번째 트림 값만 사용)
    
    # 왼쪽 테이블에서 항목명 수집 (compareLeft_*)
    left_rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='compareLeft_']")
    logger.debug(f"항목명 행 발견: {len(left_rows)}개")
    
    for left_row in left_rows:
        row_id = left_row.get_attribute("id")
        if not row_id or not row_id.startswith("compareLeft_"):
            continue
            
        # ID에서 번호 추출 (예: compareLeft_0 -> 0)
        try:
            index = int(row_id.replace("compareLeft_", ""))
        except ValueError:
            continue
        
        # 항목명 추출
        tds = left_row.find_elements(By.TAG_NAME, "td")
        if not tds:
            continue
        
        key = tds[0].text.strip()
        if not key:
            continue
        
        # 오른쪽 테이블에서 해당 인덱스의 값 추출 (compareRight_*)
        right_row_id = f"compareRight_{index}"
        try:
            right_row = driver.find_element(By.ID, right_row_id)
            right_tds = right_row.find_elements(By.TAG_NAME, "td")
            
            if right_tds:
                # 첫 번째 트림의 값 사용 (첫 번째 td)
                value_elem = right_tds[0]
                # <a> 태그나 <span> 태그 내부의 텍스트 추출
                links = value_elem.find_elements(By.TAG_NAME, "a")
                spans = value_elem.find_elements(By.TAG_NAME, "span")
                
                if links:
                    value = links[0].text.strip()
                elif spans:
                    value = spans[0].text.strip()
                else:
                    value = value_elem.text.strip()
                
                if value:
                    # 모든 제원 정보를 specs에 저장
                    data["specs"][key] = value
        except Exception as e:
            logger.debug(f"항목 '{key}' 값 추출 실패: {e}")
            continue

    # 유지비 추출 (compare__table compare__price 테이블의 "합계" 행에서)
    try:
        price_tables = driver.find_elements(By.CSS_SELECTOR, "table.compare__table.compare__price, table.compare__table.compare__body22.compare__price")
        for price_table in price_tables:
            # "합계" 텍스트가 있는 행 찾기
            sum_rows = price_table.find_elements(By.XPATH, ".//tr[.//span[contains(@class, 'price_sum')] or .//td[contains(text(), '합계')]]")
            for sum_row in sum_rows:
                # price_sum 클래스를 가진 span 요소에서 유지비 값 추출
                price_sum_spans = sum_row.find_elements(By.CSS_SELECTOR, "span.price_sum")
                for span in price_sum_spans:
                    # "합계" 텍스트가 아닌 숫자 값만 추출
                    text = span.text.strip()
                    if text and text != "합계":
                        # 숫자와 쉼표만 추출
                        price_match = re.search(r'([\d,]+)', text)
                        if price_match:
                            maintenance_cost = price_match.group(1).replace(",", "")
                            if maintenance_cost:
                                # "유지비" 또는 "유지비용" 키로 저장
                                data["specs"]["유지비"] = f"{maintenance_cost}원"
                                logger.debug(f"유지비 추출: {data['specs']['유지비']}")
                                break
                if "유지비" in data["specs"]:
                    break
            if "유지비" in data["specs"]:
                break
    except Exception as e:
        logger.debug(f"유지비 추출 중 오류 발생: {e}")

    logger.debug(f"제원 항목 추출 완료: {len(data.get('specs', {}))}개")
    if data["specs"]:
        # 중요한 항목들 로그 출력
        important_keys = ["엔진형식", "연료", "복합연비", "도심연비", "고속연비", "배기량"]
        for key in important_keys:
            if key in data["specs"]:
                logger.debug(f"  {key}: {data['specs'][key]}")
    
    return data


def extract_model_image_url(driver, model_id, search_keyword="봉고"):
    """
    다나와 검색 페이지에서 특정 model_id의 대표 이미지 URL을 추출
    
    Args:
        driver: Selenium WebDriver
        model_id: 모델 ID
        search_keyword: 검색 키워드 (기본값: "봉고")
    
    Returns:
        이미지 URL 문자열
    """
    # 여러 검색 키워드 시도 (우선순위 순서)
    search_keywords = [search_keyword]
    if "EV" in search_keyword:
        # EV 모델의 경우 여러 키워드 시도
        search_keywords = [search_keyword, "봉고3", "봉고"]
    elif "봉고3" in search_keyword:
        search_keywords = [search_keyword, "봉고"]
    
    for keyword in search_keywords:
        url = f"https://auto.danawa.com/search/?q={quote(keyword)}"
        logger.debug(f"검색 페이지 접속(이미지 추출): {url} (키워드: {keyword})")
        
        try:
            driver.get(url)
        except Exception as e:
            logger.warning(f"검색 페이지 로드 중 오류 발생 (계속 진행): {e}")
            continue
        
        time.sleep(2)
        
        # href에 Model={model_id}가 포함된 a.image 내부 img
        css = f"ul#salesNewcarList a.image[href*='Model={model_id}'] img"
        imgs = driver.find_elements(By.CSS_SELECTOR, css)
        
        if imgs:
            img_url = imgs[0].get_attribute("src") or ""
            if img_url:
                logger.info(f"이미지 URL 추출 성공: {model_id} -> {img_url} (키워드: {keyword})")
                return img_url
        
        logger.debug(f"키워드 '{keyword}'로 이미지를 찾지 못했습니다. 다음 키워드 시도...")
    
    logger.warning(f"모든 검색 키워드로 시도했지만 model_id={model_id} 이미지를 찾지 못했습니다")
    return ""


def get_all_lineups(driver, model_id):
    """모든 라인업 ID와 이름 가져오기"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Tab=price"
    logger.debug(f"라인업 목록 확인을 위한 페이지 접속 중: {url}")
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"라인업 페이지 로드 중 오류 발생 (계속 진행): {e}")
    # JavaScript 렌더링 완료를 위한 명시적 대기
    time.sleep(3)
    logger.debug("라인업 페이지 로드 완료")

    lineups = []
    radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'][name='lineup_']")
    logger.debug(f"라인업 라디오 버튼 발견: {len(radios)}개")
    
    for radio in radios:
        lineup_id = radio.get_attribute("data-lineup")
        if not lineup_id:
            logger.debug("라인업 ID가 없는 라디오 버튼 건너뜀")
            continue
        
        # 라인업 이름 추출 - div.selectbox > a.btn 구조에서 추출
        lineup_name = ""
        
        try:
            # radio의 부모 요소(div.choice)에서 selectbox 찾기
            parent = radio.find_element(By.XPATH, "./ancestor::div[contains(@class, 'choice')]")
            
            # div.selectbox > a.btn 구조 찾기
            selectbox = parent.find_elements(By.CSS_SELECTOR, ".selectbox a.btn, .selectbox > a.btn")
            if selectbox:
                # span.year 같은 자식 요소 제거하고 텍스트만 추출
                lineup_name = selectbox[0].text.strip()
                # span.year 제거 (날짜 정보)
                if lineup_name:
                    # (2026.01.06.) 같은 날짜 정보 제거
                    lineup_name = re.sub(r'\s*\([^)]*\)\s*$', '', lineup_name).strip()
            else:
                # selectbox가 없으면 label 텍스트 사용
                label_els = parent.find_elements(By.CSS_SELECTOR, f"label[for='lineup_{lineup_id}']")
                if label_els:
                    lineup_name = label_els[0].text.strip()
                else:
                    # choice__cell choice__info 안의 txt 클래스 확인
                    txt_els = parent.find_elements(By.CSS_SELECTOR, ".choice__cell.choice__info .txt")
                    if txt_els:
                        lineup_name = txt_els[0].text.strip()
        except Exception as e:
            logger.debug(f"라인업 {lineup_id} 이름 추출 중 오류: {e}")
            # 대체 방법: label에서 직접 추출
            try:
                label_els = driver.find_elements(By.CSS_SELECTOR, f"label[for='lineup_{lineup_id}']")
                if label_els:
                    lineup_name = label_els[0].text.strip()
            except Exception:
                pass
        
        if lineup_name:
            lineups.append({
                "id": lineup_id,
                "name": lineup_name
            })
            logger.debug(f"라인업 발견: {lineup_name} (ID: {lineup_id})")
        else:
            logger.warning(f"라인업 ID {lineup_id}의 이름을 찾을 수 없어 건너뜁니다")
    
    logger.info(f"총 {len(lineups)}개의 라인업 발견")
    return lineups


def crawl_model(driver, model_id, model_name, lineup_ids=None):
    """단일 모델 크롤링 - 모든 라인업 또는 지정된 라인업 수집
    
    Args:
        driver: Selenium WebDriver
        model_id: 모델 ID
        model_name: 모델 이름
        lineup_ids: 크롤링할 라인업 ID 리스트. None이면 모든 라인업 크롤링
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"크롤링 시작: {model_name} (ID: {model_id})")
    logger.info(f"{'='*50}")

    result = {
        "model": model_name,
        "model_id": model_id,
        "image_url": "",
        "lineup": []
    }
    
    # 모델 이미지 URL 추출
    try:
        logger.info("모델 이미지 URL 추출 중...")
        # 검색 키워드 결정 (봉고3 EV는 "봉고3 EV", 봉고3는 "봉고3")
        search_keyword = "봉고3 EV" if "EV" in model_name else "봉고3"
        image_url = extract_model_image_url(driver, model_id, search_keyword)
        result["image_url"] = image_url
        if image_url:
            logger.info(f"이미지 URL 추출 완료: {image_url}")
        else:
            logger.warning("이미지 URL을 찾을 수 없습니다")
    except Exception as e:
        logger.warning(f"이미지 URL 추출 중 오류 발생 (계속 진행): {e}")

    # 라인업 목록 가져오기
    try:
        if lineup_ids:
            # 지정된 라인업 ID만 사용
            logger.info(f"지정된 라인업 ID로 크롤링: {lineup_ids}")
            # 라인업 이름을 가져오기 위해 한 번 페이지 접속
            all_lineups = get_all_lineups(driver, model_id)
            lineup_map = {lu["id"]: lu["name"] for lu in all_lineups}
            
            lineups = []
            for lineup_id in lineup_ids:
                lineup_name = lineup_map.get(lineup_id, f"라인업 {lineup_id}")
                lineups.append({"id": lineup_id, "name": lineup_name})
                logger.info(f"  - {lineup_name} (ID: {lineup_id})")
        else:
            # 모든 라인업 가져오기
            logger.info("모든 라인업 수집 중...")
            lineups = get_all_lineups(driver, model_id)
        
        if not lineups:
            logger.warning("라인업을 찾을 수 없습니다")
            return result
        
        # 각 라인업별로 정보 추출
        for idx, lineup_info in enumerate(lineups, 1):
            lineup_id = lineup_info["id"]
            lineup_name = lineup_info["name"]
            
            # 라인업 ID가 없으면 건너뛰기
            if not lineup_id:
                logger.warning(f"라인업 ID가 없어 건너뜁니다: {lineup_name}")
                continue
            
            logger.info(f"\n[{idx}/{len(lineups)}] 라인업 처리 중: {lineup_name} (ID: {lineup_id})")
            
            lineup_data = {
                "id": str(lineup_id),  # 문자열로 변환
                "name": lineup_name,  # select box에서 가져온 이름
                "trims": {"name": "", "price": ""},
                "specs": {}
            }
            
            # 제원 상세 정보 추출 (트림명과 가격도 함께 추출)
            try:
                logger.info("제원 상세 정보 및 트림 정보 추출 중...")
                spec_data = extract_spec_detail(driver, model_id, lineup_id)
                
                # 트림 정보 추출 (제원·사양/옵션 탭의 테이블 헤더에서)
                if "trims" in spec_data:
                    trim_info = spec_data["trims"]
                    if trim_info.get("name") or trim_info.get("price"):
                        lineup_data["trims"]["name"] = trim_info.get("name", "")
                        lineup_data["trims"]["price"] = trim_info.get("price", "")
                        logger.info(f"트림명: {lineup_data['trims']['name']}, 가격: {lineup_data['trims']['price']}")
                
                # 트림 정보를 찾지 못한 경우 가격·제원·사양 탭에서 시도
                if not lineup_data["trims"]["name"] and not lineup_data["trims"]["price"]:
                    logger.info("제원 탭에서 트림 정보를 찾지 못해 가격 탭에서 시도...")
                    try:
                        trim_info = extract_trim_info_from_price_tab(driver, model_id, lineup_id)
                        lineup_data["trims"]["name"] = trim_info.get("name", "")
                        lineup_data["trims"]["price"] = trim_info.get("price", "")
                        if lineup_data["trims"]["name"] or lineup_data["trims"]["price"]:
                            logger.info(f"트림명: {lineup_data['trims']['name']}, 가격: {lineup_data['trims']['price']}")
                    except Exception as e:
                        logger.debug(f"가격 탭에서 트림 정보 추출 실패: {e}")
                
                # 제원 정보 추출
                if "specs" in spec_data:
                    lineup_data["specs"] = spec_data["specs"]
                    logger.info(f"제원 추출 완료: {len(lineup_data['specs'])}개 항목")
                    if "유지비" in lineup_data["specs"]:
                        logger.info(f"유지비: {lineup_data['specs']['유지비']}")
                else:
                    logger.warning("제원 정보를 찾을 수 없습니다")
                    
            except Exception as e:
                logger.error(f"라인업 {lineup_name} 정보 추출 오류: {e}", exc_info=True)
            
            result["lineup"].append(lineup_data)
            
            # 각 라인업 처리 후 잠시 대기 (서버 부하 방지)
            time.sleep(1)
        
        logger.info(f"총 {len(result['lineup'])}개의 라인업 처리 완료")
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)

    logger.info(f"크롤링 완료: {model_name}")
    return result


def main():
    """메인 실행 함수
    
    명령줄 인자:
        --lineup-ids: 크롤링할 라인업 ID를 쉼표로 구분하여 지정
        예: python crawl_bongo.py --lineup-ids 53592,53588
    """
    # 명령줄 인자 파싱
    lineup_ids_arg = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--lineup-ids" and i + 1 < len(sys.argv):
                lineup_ids_arg = [lid.strip() for lid in sys.argv[i + 1].split(",") if lid.strip()]
                logger.info(f"명령줄에서 지정된 라인업 ID: {lineup_ids_arg}")
                break
    
    logger.info("=" * 50)
    logger.info("봉고 크롤링 시작")
    logger.info(f"대상 모델: {len(BONGO_MODELS)}개")
    logger.info("=" * 50)
    
    driver = create_driver()
    all_results = {}

    try:
        for idx, (key, model_info) in enumerate(BONGO_MODELS.items(), 1):
            logger.info(f"\n[{idx}/{len(BONGO_MODELS)}] 모델 처리 중...")
            
            # 라인업 ID 결정: 명령줄 인자 > MODELS 설정 > None(모든 라인업)
            lineup_ids = lineup_ids_arg or model_info.get("lineup_ids")
            
            model_results = crawl_model(
                driver, 
                model_info["id"], 
                model_info["name"],
                lineup_ids=lineup_ids
            )
            all_results[key] = model_results
    except Exception as e:
        logger.error(f"크롤링 중 치명적 오류 발생: {e}", exc_info=True)
    finally:
        logger.info("크롬 드라이버 종료 중...")
        driver.quit()
        logger.info("크롬 드라이버 종료 완료")

    # 결과 저장
    logger.info("결과 저장 중...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        logger.info(f"결과 저장 완료: {OUTPUT_PATH}")
        logger.info(f"저장된 모델 수: {len(all_results)}개")
    except Exception as e:
        logger.error(f"결과 저장 중 오류 발생: {e}", exc_info=True)
    
    logger.info("=" * 50)
    logger.info("봉고 크롤링 종료")
    logger.info("=" * 50)
    
    return all_results


if __name__ == "__main__":
    main()
