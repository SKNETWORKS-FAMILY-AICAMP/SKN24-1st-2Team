from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
from pathlib import Path 

chromedriver_path = 'chromedriver.exe'


OUTPUT_DIR = Path(r"C:\skn24\team_project(1)\DumPs-Up\data\raw\faq")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"   Directory exists: {OUTPUT_DIR.exists()}\n")


service = webdriver.chrome.service.Service(chromedriver_path)
driver = webdriver.Chrome(service=service)


# Category Keywords
category_keywords = {
    'cost': ['비용', '보조금', '지원금', '가격', '할인', '환급', '세금', '부가세'],
    'registration': ['등록', '허가', '번호판', '검사', '운수사업', '신청', '구조변경', '명의'],
    'infrastructure': ['충전', '충전소', '주차', '주행', '운행', '배터리', '전기', '충전기'],
    'maintenance': ['정비', '수리', '고장', 'AS', 'A/S', '점검', '보증', '서비스', '교체', '부품', '정기점검', '엔진', '타이어', '오일']
}

# Fuel Type Keywords
fuel_keywords = {
    "electric": ["전기", "전기차", "전기 트럭", "EV", "배터리", "충전", "electric"],
    "hybrid": ["하이브리드", "HEV", "PHEV", "hybrid"],
    "diesel": ["디젤", "디젤차", "경유", "diesel"],
    "gasoline": ["휘발유", "가솔린", "gasoline"],
    "lpg": ["LPG", "엘피지", "lpg", "LPG차"],
    "hydrogen": ["수소", "수소차", "hydrogen", "FCEV"],
    "cng": ["CNG", "천연가스", "compressed natural gas"]
}

# Target Sites Configuration
sites = [
    # Cost Related (비용관련 - 2)
    {
        "url": "https://news.seoul.go.kr/env/archives/517115",
        "css": "strong, h3",
        "default_category": "cost",
        "default_fuel": "electric",
        "description": "Seoul Eco-friendly Truck Subsidy",
        "wait_time": 2
    },
    {
        "url": "https://navyblog.kr/중고-화물차-부가세-환급받는-방법2025년-최신-faq-포함/",
        "css": "h2, h3",
        "default_category": "cost",
        "default_fuel": "other",
        "description": "Used Truck VAT Refund",
        "wait_time": 2
    },
    
    # Registration Related (등록허가관련 - 4)
    {
        "url": "https://dabori.co.kr/화물차-적재함-구조변경-필수-faq/",
        "css": "h2, h3",
        "default_category": "registration",
        "default_fuel": "other",
        "description": "Truck Structure Modification",
        "wait_time": 2
    },
    {
        "url": "https://www.kgta.or.kr/board/faq",
        "css": ".subject, .title",
        "default_category": "registration",
        "default_fuel": "other",
        "description": "Freight Transport Business License",
        "wait_time": 3
    },
    {
        "url": "https://www.seoulta.or.kr/board/faq",
        "css": "td.subject, .title",
        "default_category": "registration",
        "default_fuel": "other",
        "description": "Seoul Trucking Association",
        "wait_time": 3
    },
    {
        "url": "https://main.kotsa.or.kr/portal/bbs/faq_list.do?pageNumb=1&menuCode=04010100",
        "css": "td.subject, .list_title",
        "default_category": "registration",
        "default_fuel": "other",
        "description": "KOTSA (Traffic Safety)",
        "wait_time": 3
    },
    
    # Infrastructure Related (인프라관련 - 2)
    {
        "url": "https://ev.or.kr/nportal/partcptn/initFaqAction.do",
        "css": "dt, .faq_tit",
        "default_category": "infrastructure",
        "default_fuel": "electric",
        "description": "EV Charging Infrastructure",
        "wait_time": 2
    },
    {
        "url": "https://www.kia.com/kr/vehicles/kia-ev/charging/faq",
        "css": "dt, .faq-item__question",
        "default_category": "infrastructure",
        "default_fuel": "electric",
        "description": "Kia EV Charging",
        "wait_time": 3
    },
    
    # Vehicle Maintenance & repair related (A/S관련)
    {
        "url": "https://www.hyundai.com/kr/ko/digital-customer-support/helpdesk/faq",
        "css": "button, .faq-item, .question-title",
        "default_category": "maintenance",
        "default_fuel": "other",
        "description": "Hyundai Customer Support FAQ",
        "wait_time": 4
    }
]


def classify_category(text):
    """Classify text into category based on keywords"""
    text_lower = text.lower()
    
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return None

def classify_fuel_type(text):
    """Classify text into fuel type based on keywords"""
    text_lower = text.lower()
    
    for fuel_type, keywords in fuel_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return fuel_type
    return None
#  ===================================
all_faqs = []

print("=" * 60)
print("Truck FAQ Crawler Started")
print("=" * 60)
print(f"Total sites to crawl: {len(sites)}\n")

for idx, site in enumerate(sites, 1):
    print(f"\n[{idx}/{len(sites)}] 📍 Crawling: {site['description']}")
    print(f"URL: {site['url']}")
    
    try:
        # Open website
        driver.get(site["url"])
        time.sleep(site["wait_time"])
        
        # Scroll to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Find question elements
        questions = driver.find_elements(By.CSS_SELECTOR, site["css"])
        print(f"Found: {len(questions)} elements")
        
        collected_count = 0
        
        for question_elem in questions:
            question_text = question_elem.text.strip()
            
            # Skip too short text
            if len(question_text) < 10:
                continue
            
            # Find answer (multiple strategies)
            answer_text = "No answer available"
            
            # Strategy 1: Try following sibling
            try:
                answer_elem = question_elem.find_element(By.XPATH, "following-sibling::*[1]")
                answer_text = answer_elem.text.strip()
            except:
                pass
            
            # Strategy 2: Try clicking if it's a button/accordion
            if answer_text == "No answer available":
                try:
                    driver.execute_script("arguments[0].click();", question_elem)
                    time.sleep(0.5)
                    answer_elem = question_elem.find_element(By.XPATH, "following-sibling::*[1]")
                    answer_text = answer_elem.text.strip()
                except:
                    pass
            
            # Strategy 3: Try parent element
            if answer_text == "No answer available":
                try:
                    parent = question_elem.find_element(By.XPATH, "..")
                    answer_elem = parent.find_element(By.CSS_SELECTOR, ".answer, .content, dd")
                    answer_text = answer_elem.text.strip()
                except:
                    pass
            
            # Skip if no meaningful answer found
            if len(answer_text) < 20:
                continue
            
            # Classify category and fuel type
            combined_text = question_text + " " + answer_text
            category = classify_category(combined_text)
            if not category:
                category = site["default_category"]
            
            fuel_type = classify_fuel_type(combined_text)
            if not fuel_type:
                fuel_type = site["default_fuel"]
            
            # Store FAQ data
            faq = {
                "category_name": category,
                "fuel_type": fuel_type,
                "question": question_text,
                "answer": answer_text,
                "source_url": site["url"]
            }
            
            all_faqs.append(faq)
            collected_count += 1
            
            # Print sample (first 3 only)
            if collected_count <= 3:
                print(f"  ✓ [{category}] {fuel_type} - {question_text[:40]}...")
        
        print(f"Collected: {collected_count} FAQs ✅")
        time.sleep(1.5)
        
    except Exception as error:
        print(f"❌ Error: {error}")


print("\n" + "=" * 60)
print("📊 Collection Results")
print("=" * 60)
print(f"Total FAQs collected: {len(all_faqs)}")

# Count by category
print("\n[By Category]")
category_stats = {}
for category in category_keywords.keys():
    count = sum(1 for faq in all_faqs if faq["category_name"] == category)
    category_stats[category] = count
    percentage = (count / len(all_faqs) * 100) if all_faqs else 0
    print(f"  - {category}: {count} ({percentage:.1f}%)")

# Count by fuel type
print("\n[By Fuel Type]")
fuel_stats = {}
for faq in all_faqs:
    fuel = faq["fuel_type"]
    fuel_stats[fuel] = fuel_stats.get(fuel, 0) + 1

for fuel, count in sorted(fuel_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(all_faqs) * 100) if all_faqs else 0
    print(f"  - {fuel}: {count} ({percentage:.1f}%)")


# Save as JSON Files
print("\n" + "=" * 60)
print("💾 Saving JSON files...")
print("=" * 60)

# Save all FAQs with metadata
output_data = {
    "metadata": {
        "total_count": len(all_faqs),
        "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "categories": category_stats,
        "fuel_types": fuel_stats,
        "output_directory": str(OUTPUT_DIR)
    },
    "faqs": all_faqs
}

all_faqs_path = OUTPUT_DIR / "all_faqs_json"
with open("all_faqs_path", "w", encoding="utf-8") as file:
    json.dump(output_data, file, ensure_ascii=False, indent=2)
print(f"✅ all_faqs.json saved to: {all_faqs_path}")

# Save by category
for category in category_keywords.keys():
    category_faqs = [faq for faq in all_faqs if faq["category_name"] == category]
    
    if category_faqs:
        filename = f"{category}_faqs.json"
        filepath = OUTPUT_DIR / filename
        category_data = {
            "category": category,
            "count": len(category_faqs),
            "faqs": category_faqs
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(category_data, file, ensure_ascii=False, indent=2)
        print(f"✅ {filename} saved to: {filepath} ({len(category_faqs)} items)")


driver.quit()

print("\n" + "=" * 60)
print("All tasks completed")
print("=" * 60)
print(f"\n All files saved to: {OUTPUT_DIR}")
print("\nSaved files:")
print(f"  - {OUTPUT_DIR / 'all_faqs.json'} (with metadata)")
print(f"  - {OUTPUT_DIR / 'cost_faqs.json'}")
print(f"  - {OUTPUT_DIR / 'registration_faqs.json'}")
print(f"  - {OUTPUT_DIR / 'infrastructure_faqs.json'}")
print(f"  - {OUTPUT_DIR / 'maintenance_faqs.json'}")