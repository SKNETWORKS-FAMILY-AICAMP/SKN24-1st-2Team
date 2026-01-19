import json
from pathlib import Path

from src.database.db_manager import DBManager

FAQ_JSON_PATH = Path("data/raw/faq/all_faqs.json")

CATEGORY_TO_DB_NAME = {
    "cost": "비용",
    "registration": "등록",
    "infrastructure": "충전",
    "maintenance": "정비",
    "기타": "기타",
    "other": "기타",
}

def get_raw_faq_data():
    with open(FAQ_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def transform_faq_data(raw: dict):
    """
    fuel처럼 transformed로 DB에 바로 넣을 '튜플 리스트'를 만든다.
    다만 FAQ는 FK(category_code)가 필요해서:
    - category_names: 카테고리명 리스트(중복 제거)
    - faqs: FAQ 원본 리스트
    두 개를 반환하고, DB에서 category_code 매핑 만든 뒤 faq_tuples 만든다.
    """
    faqs = raw.get("faqs", [])
    category_names = sorted({
        CATEGORY_TO_DB_NAME.get((f.get("category_name") or "기타").strip(), "기타")[:10]
        for f in faqs
    })
    return category_names, faqs

def load_faq_info():
    """FAQ 데이터 ETL 프로세스 실행 (fuel 구조 유지)"""
    print("[FAQ] 데이터 수집 시작...")
    raw = get_raw_faq_data()

    print("[FAQ] 데이터 가공 시작...")
    category_names, faqs = transform_faq_data(raw)

    print("[FAQ] DB 저장 시작...")
    db = DBManager()

    if not db.connect():
        return

    try:
        cursor = db.get_cursor()

        # (선택) 테이블 생성까지 여기서 보장하고 싶으면 주석 해제
        db.create_tables()

        # 1) 카테고리 먼저 넣기 (중복이면 넣지 않기)
        # 스키마에 UNIQUE가 없으니, SELECT로 존재여부 확인 후 INSERT
        sel_cat = "SELECT category_code FROM faq_category_tbl WHERE category_name=%s"
        ins_cat = "INSERT INTO faq_category_tbl (category_name) VALUES (%s)"

        for name in category_names:
            cursor.execute(sel_cat, (name,))
            if cursor.fetchone() is None:
                cursor.execute(ins_cat, (name,))

        # 2) category_name -> category_code 매핑 가져오기
        cursor.execute("SELECT category_code, category_name FROM faq_category_tbl")
        name_to_code = {name: code for (code, name) in cursor.fetchall()}

        # 3) FAQ 튜플로 변환 (fuel의 transformed 역할)
        faq_tuples = []
        for item in faqs:
            question = (item.get("question") or "").strip()
            answer = (item.get("answer") or "").strip()
            source_url = (item.get("source_url") or "").strip()
            fuel_type = (item.get("fuel_type") or "").strip().lower()

            cat_key = (item.get("category_name") or "기타").strip()
            cat_name = CATEGORY_TO_DB_NAME.get(cat_key, "기타")[:10]
            category_code = name_to_code.get(cat_name)

            if not category_code or not question or not answer or not source_url:
                continue

            related = "전기" if fuel_type in ("electric", "ev") else ("내연" if fuel_type in ("diesel","gasoline","lpg","cng","hybrid","hydrogen") else "전체")

            # VARCHAR(255) 안전
            faq_tuples.append((
                category_code,
                question[:255],
                answer[:255],
                source_url[:255],
                related[:20]
            ))

        # 4) fuel처럼 executemany로 한 번에 INSERT
        query = """
            INSERT INTO faq_tbl (category_code, question, answer, source_url, related_fuel_type)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, faq_tuples)

        db.commit()
        print(f"[FAQ] {len(faq_tuples)}건 저장 완료 ✅")

    except Exception as e:
        print(f"[FAQ] 저장 실패 ❌: {e}")
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    load_faq_info()
