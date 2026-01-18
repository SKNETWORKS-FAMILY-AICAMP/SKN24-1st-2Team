import sys
import streamlit as st
from pathlib import Path
from html import escape

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# TODO: DB 연동 시 services 폴더에서 데이터 가져오도록 수정
from src.utils.data import get_dummy_faq_category_data, get_dummy_faq_data

_dummy_categories = get_dummy_faq_category_data()
_dummy_faqs = get_dummy_faq_data()

# 카테고리 리스트
CATEGORIES = [cat[1] for cat in _dummy_categories]
SAMPLE_FAQ_DATA = {}
    
for faq_item in _dummy_faqs:
    _, category_name, question, answer, source_url, _ = faq_item
    
    if category_name not in SAMPLE_FAQ_DATA:
        SAMPLE_FAQ_DATA[category_name] = []
    
    SAMPLE_FAQ_DATA[category_name].append({
        "question": question,
        "answer": answer,
        "url": source_url
    })

# 세션 상태 초기화
if "faq_selected_category" not in st.session_state:
    st.session_state.faq_selected_category = CATEGORIES[0]

# 카테고리 선택 콜백
def select_category(category):
    st.session_state.faq_selected_category = category

st.markdown("""
<h1 class="page-title text-center">
    자주 묻는 질문
</h1>
""", unsafe_allow_html=True)

main_container = st.container(key="faq_container")
with main_container:
    sidebar_col, content_col = st.columns([1, 4])

    # ========================================
    #   왼쪽 사이드바
    # ========================================
    with sidebar_col:
        sidebar_container = st.container(key="faq_sidebar")
        with sidebar_container:
            for category in CATEGORIES:
                is_selected = st.session_state.faq_selected_category == category
                
                st.button(
                    category,
                    key=f"category_{category}",
                    on_click=select_category,
                    args=(category,),
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                )

    # ========================================
    #   오른쪽 메인 콘텐츠
    # ========================================
    with content_col:
        main_content = st.container(key="faq_main")
        with main_content:

            # 선택된 카테고리의 FAQ 표시
            selected_category = st.session_state.faq_selected_category
            faq_list = SAMPLE_FAQ_DATA.get(selected_category, [])

            for faq in faq_list:
                question_html = escape(str(faq.get("question", "")))
                answer_html = escape(str(faq.get("answer", ""))).replace("\n", "<br/>")
                url_html = escape(str(faq.get("url", "")), quote=True)

                st.markdown(
                    f"""
                    <details class="faq-item faq-details">
                        <summary>{question_html}</summary>
                        <div class="faq-content">
                            <div class="faq-content-inner">
                                <div class="faq-answer">{answer_html}</div>
                                <a href="{url_html}" class="faq-view-more" target="_blank" rel="noopener noreferrer">
                                    자세히 보기
                                </a>
                            </div>
                        </div>
                    </details>
                    """,
                    unsafe_allow_html=True,
                )
