from selenium import webdriver
from selenium.webdriver.common.by import By
import time

path = 'chromedriver.exe'
service = webdriver.chrome.service.Service(path)
driver = webdriver.Chrome(service=service)


faq_list = []

def crawl_site(url, question_css):
    driver.get(url)
    time.sleep(1.5) 

    questions = driver.find_elements(By.CSS_SELECTOR, question_css)
    
    for q in questions:
        q_text = q.text.strip()
        if len(q_text) < 10:  
            continue
        
        
        try:
            a = q.find_element(By.XPATH, "following-sibling::*[1] | ./dd | ./following::p[1]")
            a_text = a.text.strip()
        except:
            a_text = "답변 없음"
        
        faq_list.append({
            "site": url,
            "question": q_text,
            "answer": a_text
        })
        print(f"Q: {q_text[:50]}")
        print(f"A: {a_text[:100]}")
        print("---")


sites = [
    {"url": "https://news.seoul.go.kr/env/archives/517115", "css": "strong, h3"},
    {"url": "https://ev.or.kr/nportal/partcptn/initFaqAction.do", "css": "dt, .faq_tit"},
    {"url": "https://dabori.co.kr/화물차-적재함-구조변경-필수-faq/", "css": "h2, h3, strong"},
    {"url": "https://www.kgta.or.kr/board/faq", "css": ".subject, .title_cell"},
    {"url": "https://navyblog.kr/중고-화물차-부가세-환급받는-방법2025년-최신-faq-포함/", "css": "h2, h3, strong"},
    {"url": "https://www.seoulta.or.kr/board/faq", "css": "td.subject, .board_list .title"},
    {"url": "https://main.kotsa.or.kr/portal/bbs/faq_list.do?pageNumb=1&menuCode=04010100", "css": "td.subject, .list_title"},
    {"url": "https://www.kia.com/kr/vehicles/kia-ev/charging/faq", "css": ".faq-item__question, dt"}
]

print("="*50)
print("==크롤링을 시작합니다.==")
print("="*50)

for site in sites:
    print(f"\n사이트: {site['url']}")
    crawl_site(site["url"], site["css"])

print("\n" + "=" * 50)
print("크롤링 결과값")
print("=" * 50)

print("\n전체 FAQ:")
for faq in faq_list:
    print(f"[{faq['site']}] Q: {faq['question']}")
    print(f"A: {faq['answer']}\n")

with open("crawled_faq.txt", "w", encoding="utf-8") as f:
    for faq in faq_list:
        f.write(f"[{faq['site']}]\nQ: {faq['question']}\nA: {faq['answer']}\n\n")



driver.quit()

print("=" * 50)
print("크롤링을 끝냅니다.")
print("=" * 50)
