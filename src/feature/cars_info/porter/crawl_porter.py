import json
import logging
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# 모델 정보 (다나와 Model 파라미터 값)
# =========================
MODELS = {
    "porter2": {"id": "1901", "name": "현대 포터2"},
    "porter2_ev": {"id": "4399", "name": "현대 포터2 일렉트릭"},
}

OUTPUT_PATH = Path(__file__).parents[4] / "data" / "raw" / "car_info" / "porter.json"

# ✅ 이미지 다운로드까지 할지 (원하면 True로)
DOWNLOAD_IMAGES = True
IMAGE_SAVE_DIR = OUTPUT_PATH.parent / "images"  # data/raw/car_info/images


def setup_logger():
    """로거 설정"""
    logger = logging.getLogger("porter_crawler")
    logger.setLevel(logging.INFO)

    # 핸들러가 이미 있으면 추가하지 않음
    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


logger = setup_logger()


def create_driver():
    logger.info("크롬 드라이버 생성 중...")
    options = Options()
    # 필요하면 아래 옵션 켜도 됨 (서버/CI 환경)
    # options.add_argument("--headless=new")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(0)
    logger.info("크롬 드라이버 생성 완료")
    return driver


def parse_features(features_text):
    result = {}
    if not features_text:
        return result

    pattern = r"•\s*([^:：]+)\s*[:：]\s*([^•]+)"
    matches = re.findall(pattern, features_text)

    for category, content in matches:
        category = category.strip()
        content = content.strip()
        result[category] = content

    return result


# =========================
# ✅ 검색 페이지에서 모델 이미지 URL 추출
# =========================
def extract_model_image_url_from_search(driver, search_keyword, model_id):
    """
    다나와 검색 페이지에서 특정 model_id의 대표 이미지 URL(img.src)을 추출
    - search_keyword 예: "포터"
    - model_id 예: "1901", "4399"
    """
    url = f"https://auto.danawa.com/search/?q={quote(search_keyword)}"
    logger.info(f"검색 페이지 접속(이미지 추출): {url}")

    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"검색 페이지 로드 중 오류(계속 진행): {e}")

    time.sleep(2)

    # 핵심: href에 Model={model_id}가 포함된 a.image 내부 img
    css = f"ul#salesNewcarList a.image[href*='Model={model_id}'] img"
    imgs = driver.find_elements(By.CSS_SELECTOR, css)

    if not imgs:
        logger.warning(f"검색 페이지에서 model_id={model_id} 이미지(img)를 찾지 못했습니다")
        return ""

    img_url = imgs[0].get_attribute("src") or ""
    logger.info(f"이미지 URL 추출 성공: {model_id} -> {img_url}")
    return img_url


def download_image(image_url: str, save_path: Path) -> bool:
    """이미지 URL을 로컬 파일로 다운로드"""
    if not image_url:
        return False

    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(image_url, str(save_path))
        return True
    except Exception as e:
        logger.warning(f"이미지 다운로드 실패: {e}")
        return False


def extract_price_and_features(driver, model_id):
    """가격·제원·사양 탭에서 정보 추출"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Tab=price"
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"페이지 로드 중 오류 발생 (계속 진행): {e}")

    time.sleep(3)

    result = {"trims": []}

    tables = driver.find_elements(By.CSS_SELECTOR, "table.specTable")
    if not tables:
        logger.warning(f"모델 ID {model_id}: specTable을 찾을 수 없습니다")
        return result

    table = tables[0]

    captions = table.find_elements(By.TAG_NAME, "caption")
    result["year_model"] = captions[0].text if captions else ""

    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    if rows:
        first_row = rows[0]

        trim_els = first_row.find_elements(By.CSS_SELECTOR, "td.tdTitle")
        trim_name = trim_els[0].text.replace("\n", " ").strip() if trim_els else ""

        price_els = first_row.find_elements(By.CSS_SELECTOR, ".priceInfo .num.base")
        price = price_els[0].text if price_els else ""

        all_tds = first_row.find_elements(By.TAG_NAME, "td")
        features_text = all_tds[-1].text if all_tds else ""

        features_parsed = parse_features(features_text)

        result["trims"].append(
            {
                "name": trim_name,
                "price": price,
                "features_raw": features_text,
                "features": features_parsed,
            }
        )

    return result


def extract_spec_detail(driver, model_id, lineup_id):
    """제원·사양/옵션 탭에서 상세 제원 추출"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Lineup={lineup_id}&Tab=spec"
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"제원 상세 페이지 로드 중 오류 발생 (계속 진행): {e}")

    time.sleep(3)

    data = {"제원": {}, "사양": {}, "옵션": []}

    left_rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='compareLeft_']")

    for left_row in left_rows:
        row_id = left_row.get_attribute("id")
        if not row_id or not row_id.startswith("compareLeft_"):
            continue

        try:
            index = int(row_id.replace("compareLeft_", ""))
        except ValueError:
            continue

        tds = left_row.find_elements(By.TAG_NAME, "td")
        if not tds:
            continue

        key = tds[0].text.strip()
        if not key:
            continue

        right_row_id = f"compareRight_{index}"
        try:
            right_row = driver.find_element(By.ID, right_row_id)
            right_tds = right_row.find_elements(By.TAG_NAME, "td")
            if not right_tds:
                continue

            value_elem = right_tds[0]
            links = value_elem.find_elements(By.TAG_NAME, "a")
            spans = value_elem.find_elements(By.TAG_NAME, "span")

            if links:
                value = links[0].text.strip()
            elif spans:
                value = spans[0].text.strip()
            else:
                value = value_elem.text.strip()

            if value:
                data["제원"][key] = value

        except Exception:
            continue

    return data


def get_first_lineup_id(driver, model_id):
    """첫 번째(최신) 라인업 ID 가져오기"""
    url = f"https://auto.danawa.com/auto/?Work=model&Model={model_id}&Tab=price"
    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"라인업 페이지 로드 중 오류 발생 (계속 진행): {e}")

    time.sleep(3)

    radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'][name='lineup_']")

    for radio in radios:
        if radio.is_selected():
            lineup_id = radio.get_attribute("data-lineup")
            label_els = driver.find_elements(By.CSS_SELECTOR, f"label[for='lineup_{lineup_id}']")
            label_text = label_els[0].text if label_els else ""
            return lineup_id, label_text

    if radios:
        lineup_id = radios[0].get_attribute("data-lineup")
        label_els = driver.find_elements(By.CSS_SELECTOR, f"label[for='lineup_{lineup_id}']")
        label_text = label_els[0].text if label_els else ""
        return lineup_id, label_text

    logger.warning(f"모델 ID {model_id}: 라인업을 찾을 수 없습니다")
    return None, None


def crawl_model(driver, model_id, model_name):
    """단일 모델 크롤링"""
    logger.info(f"\n{'='*50}")
    logger.info(f"크롤링 시작: {model_name} (ID: {model_id})")
    logger.info(f"{'='*50}")

    result = {
        "model": model_name,
        "model_id": model_id,
        "image_url": "",
        "image_file": "",
        "year_model": "",
        "trims": [],
        "spec_detail": {},
    }

    # ✅ 1) 검색 페이지에서 이미지 URL 추출 (+ 다운로드)
    try:
        result["image_url"] = extract_model_image_url_from_search(driver, "포터", model_id)

        if DOWNLOAD_IMAGES and result["image_url"]:
            # 확장자 깔끔하게: png/jpg 등 url에서 추정, 없으면 png
            ext = (result["image_url"].split("?")[0].split(".")[-1] or "png").lower()
            if ext not in ("png", "jpg", "jpeg", "webp"):
                ext = "png"

            save_path = IMAGE_SAVE_DIR / f"{model_id}.{ext}"
            ok = download_image(result["image_url"], save_path)
            result["image_file"] = str(save_path) if ok else ""
    except Exception as e:
        logger.warning(f"이미지 처리 실패(계속 진행): {e}", exc_info=True)

    # ✅ 2) 가격·제원·사양 추출
    try:
        logger.info("가격·제원·사양 정보 추출 중...")
        price_data = extract_price_and_features(driver, model_id)
        result["year_model"] = price_data.get("year_model", "")
        result["trims"] = price_data.get("trims", [])
        logger.info(f"트림 정보 추출 완료: {len(result['trims'])}개")
        if result["year_model"]:
            logger.info(f"연식/모델: {result['year_model']}")
    except Exception as e:
        logger.error(f"가격/사양 추출 오류: {e}", exc_info=True)

    # ✅ 3) 제원 상세 추출
    try:
        logger.info("제원 상세 정보 추출 중...")
        lineup_id, lineup_name = get_first_lineup_id(driver, model_id)
        if lineup_id:
            logger.info(f"라인업: {lineup_name} (ID: {lineup_id})")
            spec_data = extract_spec_detail(driver, model_id, lineup_id)
            result["spec_detail"] = spec_data
            logger.info(f"제원 상세 추출 완료: {len(spec_data.get('제원', {}))}개 항목")
        else:
            logger.warning("라인업 ID를 찾을 수 없어 제원 상세 정보를 추출할 수 없습니다")
    except Exception as e:
        logger.error(f"제원 상세 추출 오류: {e}", exc_info=True)

    logger.info(f"크롤링 완료: {model_name}")
    return result


def main():
    logger.info("=" * 50)
    logger.info("포터 크롤링 시작")
    logger.info(f"대상 모델: {len(MODELS)}개")
    logger.info("=" * 50)

    driver = create_driver()
    all_results = {}

    try:
        for idx, (key, model_info) in enumerate(MODELS.items(), 1):
            logger.info(f"\n[{idx}/{len(MODELS)}] 모델 처리 중...")
            model_results = crawl_model(driver, model_info["id"], model_info["name"])
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
    logger.info("포터 크롤링 종료")
    logger.info("=" * 50)

    return all_results


if __name__ == "__main__":
    main()
