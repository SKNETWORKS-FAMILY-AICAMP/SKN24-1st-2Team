# -*- coding: utf-8 -*-
import time
import json
import re
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup

# =================================================================
# Configuration
# =================================================================

JSON_OUTPUT_DIR = Path('data/raw/faq')
JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SITES = [
    {
        "url": "https://news.seoul.go.kr/env/archives/517115", 
        "description": "Seoul Eco-friendly Truck Subsidy",
        "parser": "parse_seoul_news"
    },
    {
        "url": "https://navyblog.kr/중고-화물차-부가세-환급받는-방법2025년-최신-faq-포함/", 
        "description": "Used Truck VAT Refund",
        "parser": "parse_wordpress_blog"
    },
    {
        "url": "https://dabori.co.kr/화물차-적재함-구조변경-필수-faq/", 
        "description": "Truck Structure Modification",
        "parser": "parse_wordpress_blog"
    },
    {
        "url": "https://www.kgta.or.kr/board/faq", 
        "description": "Freight Transport Business License",
        "parser": "parse_kgta_style_table"
    },
    {
        "url": "https://www.seoulta.or.kr/board/faq", 
        "description": "Seoul Trucking Association",
        "parser": "parse_kgta_style_table"
    },
    {
        "url": "https://main.kotsa.or.kr/portal/bbs/faq_list.do?menuCode=04010100", 
        "description": "KOTSA (Traffic Safety)",
        "parser": "parse_kotsa"
    },
    {
        "url": "https://ev.or.kr/nportal/partcptn/initFaqAction.do", 
        "description": "EV Charging Infrastructure",
        "parser": "parse_ev_or_kr"
    },
    {
        "url": "https://www.kia.com/kr/vehicles/kia-ev/charging/faq", 
        "description": "Kia EV Charging",
        "parser": "parse_kia"
    },
    {
        "url": "https://www.hyundai.com/kr/ko/digital-customer-support/helpdesk/faq", 
        "description": "Hyundai Customer Support FAQ",
        "parser": "parse_hyundai"
    }
]

# =================================================================
# Classification Functions
# =================================================================

def classify_category(text):
    text_lower = text.lower()
    category_keywords = {
        'cost': ['비용', '보조금', '지원금', '가격', '할인', '환급', '세금', '부가세', '요금'],
        'registration': ['등록', '허가', '번호판', '검사', '운수사업', '신청', '구조변경', '명의', '가입', '해지', '변경'],
        'infrastructure': ['충전', '충전소', '주차', '주행', '운행', '배터리', '전기', '충전기', '인프라'],
        'maintenance': ['정비', '수리', '고장', 'AS', 'A/S', '점검', '보증', '서비스', '교체', '부품', '정기점검', '엔진', '타이어', '오일']
    }
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return '기타'

def classify_fuel_type(text):
    text_lower = text.lower()
    fuel_keywords = {
        "electric": ["전기", "전기차", "전기 트럭", "ev", "배터리", "충전"],
        "hybrid": ["하이브리드", "hev", "phev"],
        "diesel": ["디젤", "디젤차", "경유"],
        "gasoline": ["휘발유", "가솔린"],
        "lpg": ["lpg", "엘피지"],
        "hydrogen": ["수소", "수소차", "fcev"],
        "cng": ["cng", "천연가스"]
    }
    for fuel_type, keywords in fuel_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return fuel_type
    return 'other'

# =================================================================
# Parser Functions
# =================================================================

### Simple Parsers (take soup object) ###

def parse_seoul_news(soup):
    faqs = []
    qna_containers = soup.select('.qna_cont')
    for container in qna_containers:
        question_tag = container.select_one('.qlist a')
        answer_tag = container.select_one('.alist')
        if question_tag and answer_tag:
            question = question_tag.get_text(strip=True).replace("Q. ", "")
            answer = answer_tag.get_text("\n", strip=True)
            faqs.append({"question": question, "answer": answer})
    return faqs

def parse_wordpress_blog(soup):
    faqs = []
    content_area = soup.select_one('.entry-content')
    if not content_area:
        return []
    
    headings = content_area.select('h2, h3, h4')
    for heading in headings:
        question = heading.get_text(strip=True)
        answer_parts = []
        next_sibling = heading.find_next_sibling()
        while next_sibling and next_sibling.name not in ['h2', 'h3', 'h4']:
            answer_parts.append(next_sibling.get_text("\n", strip=True))
            next_sibling = next_sibling.find_next_sibling()
        
        if question and answer_parts:
            answer = "\n".join(answer_parts).strip()
            faqs.append({"question": question, "answer": answer})
    return faqs

def parse_kgta_style_table(soup):
    faqs = []
    question_divs = soup.select('.faq_list')
    for q_div in question_divs:
        question_text = q_div.get_text(strip=True)
        answer_div = q_div.find_next_sibling('div', class_='faq_answer')
        if question_text and answer_div:
            answer_text = answer_div.get_text("\n", strip=True)
            question = re.sub(r'^Q\s*', '', question_text).strip()
            faqs.append({"question": question, "answer": answer_text})
    return faqs

def parse_kia(soup):
    faqs = []
    accordion_items = soup.select('.cmp-accordion__item')
    for item in accordion_items:
        question_tag = item.select_one('.cmp-accordion__title')
        answer_tag = item.select_one('.cmp-accordion__panel')
        if question_tag and answer_tag:
            question = question_tag.get_text(strip=True)
            answer = answer_tag.get_text("\n", strip=True)
            faqs.append({"question": question, "answer": answer})
    return faqs

### Complex Parsers (take driver object) ###

def parse_hyundai(driver):
    faqs = []
    print("  - Handling pagination for Hyundai...")
    while True:
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result_area dl')))
            
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            faq_items = soup.select('div.result_area div.ui_accordion dl')
            for item in faq_items:
                question_tag = item.select_one('dt .brief')
                answer_tag = item.select_one('dd .exp')
                if question_tag and answer_tag:
                    question = question_tag.get_text(strip=True)
                    answer = answer_tag.get_text("\n", strip=True)
                    if question and answer:
                         faqs.append({"question": question, "answer": answer})
            
            next_button = driver.find_element(By.CSS_SELECTOR, 'nav.pagination button.navi.next')
            if 'disabled' in next_button.get_attribute('class') or not next_button.is_enabled():
                print("  - 'Next' button is disabled. Pagination finished.")
                break
            
            print("  - Clicking 'next' page.")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            
        except (NoSuchElementException, TimeoutException):
            print("  - No more 'next' buttons or list not found. Pagination finished.")
            break
        except Exception as e:
            print(f"  - An error occurred during Hyundai pagination: {e}")
            break
            
    unique_faqs = {faq['question']: faq for faq in faqs}.values()
    return list(unique_faqs)


def parse_ev_or_kr(driver):
    faqs = []
    print("  - Handling pagination for ev.or.kr...")
    
    wait = WebDriverWait(driver, 15)

    # Correctly extract total pages
    total_pages = 1
    try:
        # Find all numbered page links and get the max number
        page_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#pageingPosition a[id]')))
        if page_links:
            max_page_num = 0
            for link in page_links:
                try:
                    page_id = int(link.get_attribute('id'))
                    if page_id > max_page_num:
                        max_page_num = page_id
                except ValueError:
                    continue # Ignore non-integer ids
            total_pages = max_page_num if max_page_num > 0 else 1
        print(f"  - Total pages identified: {total_pages}")
    except Exception as e:
        print(f"  - Could not determine total pages, defaulting to 1. Error: {e}")

    for page_num in range(1, total_pages + 1):
        try:
            print(f"  - Scraping page {page_num}/{total_pages}...")
            
            if page_num > 1:
                # Execute JavaScript to go to the specific page
                driver.execute_script(f"goPage('statsList', 10, {page_num});")
                # Wait for the current page number to change to ensure navigation occurred
                wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#pageingPosition a.current'), str(page_num)))
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.board_faq")))
                time.sleep(1) # Add a small sleep just in case elements are rendered quickly but not fully stable
            
            # Click all FAQ titles to expand them using JavaScript
            try:
                faq_titles_to_click = driver.find_elements(By.CSS_SELECTOR, "div.board_faq .faq_title")
                print(f"  - Found {len(faq_titles_to_click)} FAQ titles to click.")
                for i in range(len(faq_titles_to_click)): # Iterate by index to handle StaleElementReferenceException
                    try:
                        # Re-find the element in each iteration if necessary to avoid StaleElementReferenceException
                        current_title_element = driver.find_elements(By.CSS_SELECTOR, "div.board_faq .faq_title")[i]
                        driver.execute_script("arguments[0].click();", current_title_element)
                    except StaleElementReferenceException:
                        print(f"  - Stale element encountered while clicking FAQ title {i}, retrying element find and click.")
                        current_title_element = driver.find_elements(By.CSS_SELECTOR, "div.board_faq .faq_title")[i] # Re-find
                        driver.execute_script("arguments[0].click();", current_title_element)
                    except Exception as click_e:
                        print(f"  - Error executing JavaScript click for FAQ title {i}: {click_e}")
                time.sleep(1) # Give time for all answers to render after clicks
            except Exception as e:
                print(f"  - Error finding or clicking FAQ titles: {e}")

            # After clicking, get the updated page source
            # No need for BeautifulSoup for this part, use Selenium directly
            faq_elements = driver.find_elements(By.CSS_SELECTOR, 'div.board_faq') # Re-find as WebElements

            if not faq_elements:
                print(f"  - No FAQ elements found on page {page_num}. Breaking.")
                break
            
            # Print a debug message to confirm content visibility
            # Let's try to get the text of the first FAQ item's title and answer using Selenium
            try:
                first_q_text = faq_elements[0].find_element(By.CSS_SELECTOR, '.faq_title > div.title').text
                first_a_text = faq_elements[0].find_element(By.CSS_SELECTOR, '.faq_con > div:nth-of-type(2)').text
                print(f"  - DEBUG: First FAQ Q: {first_q_text[:50]}...")
                print(f"  - DEBUG: First FAQ A: {first_a_text[:50]}...")
            except Exception as debug_e:
                print(f"  - DEBUG: Could not get text for first FAQ item: {debug_e}")


            for item_element in faq_elements: # Iterate through Selenium WebElements
                try:
                    question_element = item_element.find_element(By.CSS_SELECTOR, '.faq_title > div.title')
                    answer_element = item_element.find_element(By.CSS_SELECTOR, '.faq_con > div:nth-of-type(2)')
                    
                    question = question_element.text.strip()
                    answer = answer_element.text.strip()

                    if question and answer:
                        faqs.append({"question": question, "answer": answer})
                except NoSuchElementException:
                    print(f"  - Question or answer element not found in an FAQ item using new selectors.")
                    continue
                except Exception as e:
                    print(f"  - Error processing an FAQ item with Selenium using new selectors: {e}")
                    continue

        except TimeoutException:
            print(f"  - Timeout waiting for elements on page {page_num}. Moving to next.")
            # If timeout, it means the content might not be loading, so break
            break
        except Exception as e:
            print(f"  - An unexpected error occurred during ev.or.kr scraping on page {page_num}: {e}")
            break

    unique_faqs = {faq['question']: faq for faq in faqs}.values()
    return list(unique_faqs)

    unique_faqs = {faq['question']: faq for faq in faqs}.values()
    return list(unique_faqs)

def parse_kotsa(driver):
    faqs = []
    print("  - Handling pagination for KOTSA...")
    
    # Get total pages from the initial load
    wait = WebDriverWait(driver, 20) # Keep 20s wait
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-bbssearch="page"]')))
    
    soup_initial = BeautifulSoup(driver.page_source, 'lxml')
    total_pages_text = soup_initial.select_one('div[data-bbssearch="page"] p').get_text(strip=True)
    total_pages_match = re.search(r'페이지\s*(\d+)/(\d+)', total_pages_text)
    total_pages = int(total_pages_match.group(2)) if total_pages_match else 1
    print(f"  - KOTSA total pages identified: {total_pages}")

    for page_num in range(1, total_pages + 1): # Loop from 1 to total_pages
        print(f"  - Scraping page {page_num}/{total_pages}...")
        try:
            if page_num > 1:
                # Correct JavaScript function for pagination is setPage(pageNumb)
                driver.execute_script(f"setPage({page_num});")
                time.sleep(1) # Reduced from 3 to 1
            
            # Wait for the FAQ list to be present and (hopefully) updated
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-bbslist="faq"] ul')))

            soup = BeautifulSoup(driver.page_source, 'lxml')
            faq_items = soup.select('div[data-bbslist="faq"] > ul > li')

            if not faq_items:
                print("  - No FAQ items found on current page. Breaking loop.")
                break

            for item in faq_items:
                question_tag = item.select_one('a') # Corrected selector
                answer_tag = item.select_one('div[data-bbsbody="conts"]') # Corrected selector
                if question_tag and answer_tag:
                    question_text = re.sub(r'^\\[.*?\\]\s*', '', question_tag.get_text(strip=True))
                    answer_text = answer_tag.get_text("\n", strip=True)
                    faqs.append({"question": question_text, "answer": answer_text})
        except Exception as e:
            print(f"  - An error occurred during KOTSA scraping on page {page_num}: {e}")
            break
            
    unique_faqs = {faq['question']: faq for faq in faqs}.values()
    return list(unique_faqs)

# =================================================================
# Main Crawler Script
# =================================================================

def main():
    all_faqs = []
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    
    print("=" * 60)
    print("🚚 FAQ Crawler Started")
    print("=" * 60)

    try:
        for idx, site in enumerate(SITES, 1):
            print(f"\n[{idx}/{len(SITES)}] 🌐 Processing: {site['description']}")
            site_faqs = []
            try:
                driver.get(site["url"])
                time.sleep(3)
                


                parser_func = globals().get(site['parser'])
                if not parser_func:
                    print(f"  ❌ Parser function '{site['parser']}' not found. Skipping.")
                    continue

                # Pass driver to complex parsers, soup to simple ones
                if site['parser'] in ['parse_hyundai', 'parse_ev_or_kr', 'parse_kotsa']:
                    site_faqs = parser_func(driver)
                else:
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    site_faqs = parser_func(soup)

                processed_faqs = []
                for faq in site_faqs:
                    combined_text = faq['question'] + " " + faq['answer']
                    faq['category_name'] = classify_category(combined_text)
                    faq['fuel_type'] = classify_fuel_type(combined_text)
                    faq['source_url'] = site['url']
                    processed_faqs.append(faq)
                
                all_faqs.extend(processed_faqs)
                print(f"  ✅ Parsed and processed {len(processed_faqs)} FAQs from this site.")

            except Exception as e:
                print(f"  ❌ Failed to process {site['description']}. Error: {e}")

    finally:
        driver.quit()
        if os.path.exists("hyundai_debug.html"):
            os.remove("hyundai_debug.html")
        if os.path.exists("ev_or_kr_debug.html"):
            os.remove("ev_or_kr_debug.html")

    print("\n" + "=" * 60)
    print("💾 Saving JSON file...")
    
    # Deduplicate across all sources before saving
    final_unique_faqs = list({faq['question']: faq for faq in all_faqs}.values())

    output_data = {
        "metadata": {
            "total_faqs_collected": len(final_unique_faqs),
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "faqs": final_unique_faqs
    }

    all_faqs_path = JSON_OUTPUT_DIR / "all_faqs.json"
    with open(all_faqs_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, ensure_ascii=False, indent=2)
    print(f"✅ all_faqs.json saved with {len(final_unique_faqs)} total unique entries.")
    
    print("\n" + "=" * 60)
    print("🎉 All tasks completed.")
    print("=" * 60)

if __name__ == '__main__':
    main()
