import streamlit as st
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.components.korea_map import render_map_section
from src.components.charts import render_registration_trend_chart, render_maintenance_cost_chart

# TODO: DB 연동 시 services 폴더에서 데이터 가져오도록 수정
from src.utils.data import (
    REGISTRATION_TREND_DATA,
    MAINTENANCE_COST_DATA,
    get_paldo_charging_data,
    get_paldo_ratio_data,
)


# 타이틀
st.markdown("""
<h1 class="page-title">
    통계 및 현황
</h1>
""", unsafe_allow_html=True)

# ========================================
#   전국 지도
# ========================================

# 기본값(전기차 충전소 현황)
if "map_filter" not in st.session_state:
    st.session_state.map_filter = "charging"

# 필터 변경 콜백
def set_map_filter(filter_type):
    st.session_state.map_filter = filter_type

# 지도 필터 버튼
with st.container(key="filter_tabs"):
    charging_col, ratio_col, col_space = st.columns([1, 1, 6])
    with charging_col:
        st.button(
            "전기차 충전소 현황",
            key="charging",
            use_container_width=True,
            type="primary" if st.session_state.map_filter == "charging" else "secondary",
            on_click=set_map_filter,
            args=("charging",)
        )

    with ratio_col:
        st.button(
            "전기 화물차 비중",
            key="ratio",
            use_container_width=True,
            type="primary" if st.session_state.map_filter == "ratio" else "secondary",
            on_click=set_map_filter,
            args=("ratio",)
        )

# 지도
filter_type = st.session_state.map_filter
if filter_type == "charging":
    card_title = "전국 전기차 충전소 현황"
    legend_text = "충전소 수"
    df = get_paldo_charging_data()
else:
    card_title = "전국 전기 화물차 비중"
    legend_text = "화물차 비중"
    df = get_paldo_ratio_data()

# 지도 컨테이너
with st.container(key="map_container"):
    st.markdown(f"""
    <div class="map-header-overlay">
        <span class="map-title">{card_title}</span>
        <span class="map-subtitle">2025년 기준</span>
    </div>
    <div class="map-legend-overlay">
        <span class="legend-dot"></span>
        <span class="legend-text">{legend_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 지도 렌더링
    render_map_section(df, filter_type)


registration_col, maintenance_col = st.columns(2)

# ========================================
#   화물차 등록 추이
# ========================================
with registration_col:
    with st.container(key="chart_card_trend"):
        st.markdown("""
        <div class="chart-header">
            <h3 class="chart-title">화물차 등록 추이</h3>
            <p class="chart-subtitle">전기 vs 내연기관 (대)</p>
        </div>
        """, unsafe_allow_html=True)

        fig_trend = render_registration_trend_chart(REGISTRATION_TREND_DATA)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

# ========================================
#   연간 유지비 비교
# ========================================
with maintenance_col:
    with st.container(key="chart_card_cost"):
        st.markdown("""
        <div class="chart-header">
            <h3 class="chart-title">연간 유지비 비교</h3>
            <p class="chart-subtitle">전기 vs 내연기관 (만원)</p>
        </div>
        """, unsafe_allow_html=True)

        fig_cost = render_maintenance_cost_chart(MAINTENANCE_COST_DATA)
        st.plotly_chart(fig_cost, use_container_width=True, config={'displayModeBar': False})
