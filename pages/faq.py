import sys
import re
import streamlit as st
from pathlib import Path
from html import escape

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.database.db_manager import DBManager  # DBManager 직접 사용


# ----------------------------------------
# 텍스트 정리(과도한 개행/기호 줄바꿈 제거)
# ----------------------------------------
def normalize_answer(text: str) -> str:
    if text is None:
        return ""

    s = str(text)

    # 1) 괄호/문장부호 주변의 이상한 개행 제거
    s = s.replace("\n(\n", " (")
    s = s.replace("\n)\n", ") ")
    s = s.replace("\n,\n", ", ")
    s = s.replace("\n.\n", ". ")
    s = s.replace("\n:\n", ": ")
    s = s.replace("\n;\n", "; ")

    # 2) 남은 개행은 공백으로(문장이 자연스럽게 이어지게)
    s = re.sub(r"\s*\n\s*", " ", s)

    # 3) 공백 정리
    s = re.sub(r"[ \t]{2,}", " ", s).strip()

    return s


# ----------------------------------------
# DB 조회 함수 (faq.py 안에 바로 작성)
# ----------------------------------------
@st.cache_data(ttl=60)
def fetch_categories_from_db():
    db = DBManager()
    if not db.connect():
        return []

    try:
        cursor = db.get_cursor()
        cursor.execute("""
            SELECT category_code, category_name
            FROM faq_category_tbl
            ORDER BY category_code DESC 
        """)
        return cursor.fetchall()
    finally:
        db.close()


@st.cache_data(ttl=60)
def fetch_faqs_from_db_by_category_name(category_name: str):
    """
    returns: [{"question":..., "answer":..., "url":...}, ...]
    """
    db = DBManager()
    if not db.connect():
        return []

    try:
        cursor = db.get_cursor()
        query = """
            SELECT f.question, f.answer, f.source_url
            FROM faq_tbl f
            JOIN faq_category_tbl c ON f.category_code = c.category_code
            WHERE c.category_name = %s
            ORDER BY f.faq_id DESC
        """
        cursor.execute(query, (category_name,))
        rows = cursor.fetchall()
        return [{"question": q, "answer": a, "url": u} for (q, a, u) in rows]
    finally:
        db.close()


# ----------------------------------------
# 카테고리/FAQ 로딩
# ----------------------------------------
categories_rows = fetch_categories_from_db()
CATEGORIES = [row[1] for row in categories_rows] if categories_rows else []

st.markdown("""
<h1 class="page-title text-center">
    자주 묻는 질문
</h1>
""", unsafe_allow_html=True)

if not CATEGORIES:
    st.error("FAQ 카테고리를 DB에서 불러오지 못했습니다. (DB 연결/DB_NAME/계정/권한/테이블 존재 여부 확인)")
    st.stop()

# 세션 상태 초기화
if "faq_selected_category" not in st.session_state:
    st.session_state.faq_selected_category = CATEGORIES[0]


def select_category(category):
    st.session_state.faq_selected_category = category


main_container = st.container(key="faq_container")
with main_container:
    sidebar_col, content_col = st.columns([1, 4])

    # 왼쪽 사이드바
    with sidebar_col:
        sidebar_container = st.container(key="faq_sidebar")
        with sidebar_container:
            for category in CATEGORIES:
                is_selected = (st.session_state.faq_selected_category == category)
                st.button(
                    category,
                    key=f"category_{category}",
                    on_click=select_category,
                    args=(category,),
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                )

    # 오른쪽 메인 콘텐츠
    with content_col:
        main_content = st.container(key="faq_main")
        with main_content:
            selected_category = st.session_state.faq_selected_category
            faq_list = fetch_faqs_from_db_by_category_name(selected_category)

            if not faq_list:
                st.info("이 카테고리에 등록된 FAQ가 없습니다.")
            else:
                for faq in faq_list:
                    question_html = escape(str(faq.get("question", "")))

                    raw_answer = faq.get("answer", "")
                    clean_answer = normalize_answer(raw_answer)
                    answer_html = escape(clean_answer).replace("\n", "<br/>")  # (거의 안 남겠지만 안전)

                    url = str(faq.get("url", "")).strip()
                    url_html = escape(url, quote=True)

                    st.markdown(
                        f"""
                        <details class="faq-item faq-details">
                            <summary>{question_html}</summary>
                            <div class="faq-content">
                                <div class="faq-content-inner">
                                    <div class="faq-answer">{answer_html}</div>
                                    {"<a href=\"" + url_html + "\" class=\"faq-view-more\" target=\"_blank\" rel=\"noopener noreferrer\">자세히 보기</a>" if url else ""}
                                </div>
                            </div>
                        </details>
                        """,
                        unsafe_allow_html=True,
                    )
