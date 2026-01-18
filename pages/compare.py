import sys
from pathlib import Path

import streamlit as st

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.utils.data import get_dummy_car_info_data, image_html


def _format_price_krw(price):
    if not price:
        return "-"
    return f"₩{price:,}"

def _car_records():
    rows = get_dummy_car_info_data()
    records = []
    for r in rows:
        fuel_type, name, maker, size, capacity, h_power, max_fuel, cx_efc, ct_efc, hw_efc, max_dist, price, image = r
        records.append(
            {
                "fuel_type": fuel_type,
                "name": name,
                "maker": maker,
                "size": size,
                "capacity": float(capacity) if capacity is not None else 0.0,
                "h_power": int(h_power) if h_power is not None else 0,
                "max_fuel": float(max_fuel) if max_fuel is not None else 0.0,
                "cx_efc": float(cx_efc) if cx_efc is not None else 0.0,
                "ct_efc": float(ct_efc) if ct_efc is not None else 0.0,
                "hw_efc": float(hw_efc) if hw_efc is not None else 0.0,
                "max_dist": int(max_dist) if max_dist is not None else 0,
                "price": int(price) if price is not None else 0,
                "image": image,
            }
        )
    return records


def _family_from_name(name):
    """차량 이름에서 계열(봉고3, 포터) 추출"""
    if not name:
        return None
    if "봉고" in name:
        return "봉고3"
    if "포터" in name:
        return "포터"
    return None


def _is_ev(record):
    """전기차 여부 판별"""
    return record.get("fuel_type") == "전기"


def _cars_by_family_and_type(records):
    """
    계열별로 일반(경유)과 EV(전기)를 분리하여 반환
    구조: {
        "봉고3": {"일반": [...], "EV": [...]},
        "포터": {"일반": [...], "EV": [...]}
    }
    """
    families = {
        "봉고3": {"일반": [], "EV": []},
        "포터": {"일반": [], "EV": []}
    }
    for rec in records:
        fam = _family_from_name(rec["name"])
        if fam in families:
            if _is_ev(rec):
                families[fam]["EV"].append(rec)
            else:
                families[fam]["일반"].append(rec)
    # 보기 좋게 정렬(가격 순)
    for fam in families:
        families[fam]["일반"] = sorted(families[fam]["일반"], key=lambda x: (x["price"], x["name"]))
        families[fam]["EV"] = sorted(families[fam]["EV"], key=lambda x: (x["price"], x["name"]))
    return families


def _get_car_record(records, car_name):
    for rec in records:
        if rec.get("name") == car_name:
            return rec
    return None


def _render_compare_card(*, key, title, subtitle, car_options, selected_name):
    selected = next((c for c in car_options if c.get("name") == selected_name), None) if car_options else None
    if not selected and car_options:
        selected = car_options[0]

    capacity = float(selected.get("capacity", 0.0)) if selected else 0.0
    max_dist = int(selected.get("max_dist", 0)) if selected else 0
    image_tag = image_html(selected.get("image") if selected else None, alt=selected.get("name", "") if selected else "")

    with st.container(key=key):
        left, mid, right = st.columns([2.6, 1.5, 1.6], vertical_alignment="center")

        with left:
            st.markdown(f'<div class="compare-image">{image_tag}</div>', unsafe_allow_html=True)

        with mid:
            st.markdown(
                f"""
                <div class="compare-metrics">
                  <div class="compare-metric">
                    <div class="compare-metric-value">{capacity:g} t</div>
                    <div class="compare-metric-label">적재량</div>
                  </div>
                  <div class="compare-metric">
                    <div class="compare-metric-value">{max_dist:,} km</div>
                    <div class="compare-metric-label">최대 주행거리</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            options = [c["name"] for c in car_options] if car_options else ["(데이터 없음)"]
            idx = options.index(selected["name"]) if selected and selected.get("name") in options else 0

            picked = st.selectbox(
                "모델",
                options,
                index=idx,
                key=f"{key}_model_select",
                label_visibility="collapsed",
            )

            picked_rec = next((c for c in car_options if c["name"] == picked), None)
            price_text = _format_price_krw(picked_rec["price"]) if picked_rec else "-"
            fuel_text = picked_rec["fuel_type"] if picked_rec else "-"

            st.markdown(
                f"""
                <div class="compare-meta">
                  <div class="compare-meta-title">{picked}</div>
                  <div class="compare-meta-sub">{fuel_text} · {price_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    return picked


def _render_detail_page(records, model_a_name, model_b_name):
    model_a = _get_car_record(records, model_a_name)
    model_b = _get_car_record(records, model_b_name)

    if not model_a or not model_b:
        st.error("차량 정보를 찾을 수 없습니다.")
        return

    # 뒤로가기 버튼
    if st.button("← 차량 비교 돌아가기", key="detail_back"):
        st.session_state.compare_show_detail = False
        st.rerun()

    st.markdown(
        """
        <h1 class="page-title">
          차량 상세 비교
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # 상단 차량 정보 카드 (2열)
    col1, col_space, col2 = st.columns([1, 0.1, 1])

    with col1:
        with st.container():
            image_tag_a = image_html(model_a.get("image"), alt=model_a.get("name", ""))
            st.markdown(
                f"""
                <div class="compare-detail-card">
                  <div class="compare-detail-card-image">
                    {image_tag_a}
                  </div>
                  <div class="compare-detail-card-title">
                    {model_a.get("name", "-")}
                  </div>
                  <div class="compare-detail-card-subtitle">
                    {model_a.get("maker", "-")} · {model_a.get("fuel_type", "-")}
                  </div>
                  <div class="compare-detail-card-price">
                    {_format_price_krw(model_a.get("price", 0))}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        with st.container():
            image_tag_b = image_html(model_b.get("image"), alt=model_b.get("name", ""))
            st.markdown(
                f"""
                <div class="compare-detail-card">
                  <div class="compare-detail-card-image">
                    {image_tag_b}
                  </div>
                  <div class="compare-detail-card-title">
                    {model_b.get("name", "-")}
                  </div>
                  <div class="compare-detail-card-subtitle">
                    {model_b.get("maker", "-")} · {model_b.get("fuel_type", "-")}
                  </div>
                  <div class="compare-detail-card-price">
                    {_format_price_krw(model_b.get("price", 0))}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)

    # 비교 테이블 (이모티콘 제거, 두 개로 분리)
    st.markdown('<h2 class="compare-section-title">사양 정보</h2>', unsafe_allow_html=True)

    comparison_labels = [
        "연료 타입",
        "제조사",
        "차량 등급",
        "적재량",
        "최대 마력",
        "연료 용량",
        "최대 주행거리",
    ]

    comparison_values_a = [
        model_a.get("fuel_type", "-"),
        model_a.get("maker", "-"),
        model_a.get("size", "-"),
        f"{model_a.get('capacity', 0):g} 톤",
        f"{model_a.get('h_power', 0)} hp",
        f"{model_a.get('max_fuel', 0):g} kWh" if model_a.get("fuel_type") == "전기" else f"{model_a.get('max_fuel', 0):g} L",
        f"{model_a.get('max_dist', 0):,} km",
    ]

    comparison_values_b = [
        model_b.get("fuel_type", "-"),
        model_b.get("maker", "-"),
        model_b.get("size", "-"),
        f"{model_b.get('capacity', 0):g} 톤",
        f"{model_b.get('h_power', 0)} hp",
        f"{model_b.get('max_fuel', 0):g} kWh" if model_b.get("fuel_type") == "전기" else f"{model_b.get('max_fuel', 0):g} L",
        f"{model_b.get('max_dist', 0):,} km",
    ]

    col1, col_space, col2 = st.columns([1, 0.1, 1])

    with col1:
        table_html_a = '<div class="compare-spec-table-container"><table class="compare-spec-table"><thead><tr><th>사양</th><th>값</th></tr></thead><tbody>'
        
        for label, value in zip(comparison_labels, comparison_values_a):
            table_html_a += f'<tr><td>{label}</td><td>{value}</td></tr>'
        
        table_html_a += '</tbody></table></div>'
        st.markdown(table_html_a, unsafe_allow_html=True)

    with col2:
        table_html_b = '<div class="compare-spec-table-container"><table class="compare-spec-table"><thead><tr><th>사양</th><th>값</th></tr></thead><tbody>'
        
        for label, value in zip(comparison_labels, comparison_values_b):
            table_html_b += f'<tr><td>{label}</td><td>{value}</td></tr>'
        
        table_html_b += '</tbody></table></div>'
        st.markdown(table_html_b, unsafe_allow_html=True)

    st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)

    # 연비 정보
    st.markdown('<h2 class="compare-section-title">연비 정보</h2>', unsafe_allow_html=True)

    col1, col_space, col2 = st.columns([1, 0.1, 1])

    with col1:
        cx_efc = model_a.get("cx_efc", 0) or 0
        ct_efc = model_a.get("ct_efc", 0) or 0
        hw_efc = model_a.get("hw_efc", 0) or 0
        unit = "km/kWh" if model_a.get("fuel_type") == "전기" else "km/L"

        st.markdown(
            f"""
            <div class="compare-fuel-card">
              <div class="compare-fuel-card-title">
                {model_a.get("name", "-")}
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">복합 연비</span>
                <span class="compare-fuel-item-value">{cx_efc:g} {unit}</span>
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">도심 연비</span>
                <span class="compare-fuel-item-value">{ct_efc:g} {unit}</span>
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">고속도로 연비</span>
                <span class="compare-fuel-item-value">{hw_efc:g} {unit}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        cx_efc = model_b.get("cx_efc", 0) or 0
        ct_efc = model_b.get("ct_efc", 0) or 0
        hw_efc = model_b.get("hw_efc", 0) or 0
        unit = "km/kWh" if model_b.get("fuel_type") == "전기" else "km/L"

        st.markdown(
            f"""
            <div class="compare-fuel-card">
              <div class="compare-fuel-card-title">
                {model_b.get("name", "-")}
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">복합 연비</span>
                <span class="compare-fuel-item-value">{cx_efc:g} {unit}</span>
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">도심 연비</span>
                <span class="compare-fuel-item-value">{ct_efc:g} {unit}</span>
              </div>
              <div class="compare-fuel-item">
                <span class="compare-fuel-item-label">고속도로 연비</span>
                <span class="compare-fuel-item-value">{hw_efc:g} {unit}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================
# Page
# =========================

records = _car_records()
families = _cars_by_family_and_type(records)

# 세션 상태 초기화
if "compare_vehicle_type" not in st.session_state:
    st.session_state.compare_vehicle_type = "봉고3"

if "compare_show_detail" not in st.session_state:
    st.session_state.compare_show_detail = False

selected_family = st.session_state.compare_vehicle_type

# 선택된 계열의 일반/EV 차량 리스트
normal_cars = families.get(selected_family, {}).get("일반", [])
ev_cars = families.get(selected_family, {}).get("EV", [])

if "compare_model_top" not in st.session_state:
    st.session_state.compare_model_top = normal_cars[0].get("name") if normal_cars else ""
if "compare_model_bottom" not in st.session_state:
    st.session_state.compare_model_bottom = ev_cars[0].get("name") if ev_cars else ""

# 계열 변경 시 모델 초기화
if "compare_prev_family" not in st.session_state:
    st.session_state.compare_prev_family = selected_family

if st.session_state.compare_prev_family != selected_family:
    st.session_state.compare_model_top = normal_cars[0].get("name") if normal_cars else ""
    st.session_state.compare_model_bottom = ev_cars[0].get("name") if ev_cars else ""
    st.session_state.compare_prev_family = selected_family

# 상세보기 모드일 경우
if st.session_state.compare_show_detail:
    _render_detail_page(
        records=records,
        model_a_name=st.session_state.compare_model_top,
        model_b_name=st.session_state.compare_model_bottom,
    )
else:
    # 일반 비교 페이지
    st.markdown(
        """
    <h1 class="page-title">
      차량 비교
    </h1>
    """,
        unsafe_allow_html=True,
    )
    
    st.markdown('<div class="compare-layout-anchor"></div>', unsafe_allow_html=True)
    main_col, sidebar_col = st.columns([5.2, 1.8], vertical_alignment="top")

    with sidebar_col:
        st.markdown('<div style="height: 1.25rem"></div>', unsafe_allow_html=True)
        with st.container(key="compare_sidebar"):
            st.markdown(
                """
                <div class="compare-sidebar-title">
                  어떤 차량 계열을 비교할까요?
                </div>
                """,
                unsafe_allow_html=True,
            )

            def _set_family(fam):
                st.session_state.compare_vehicle_type = fam

            st.button(
                "봉고",
                key="compare_pick_bongo",
                use_container_width=True,
                type="primary" if selected_family == "봉고" else "secondary",
                on_click=_set_family,
                args=("봉고",),
            )
            st.button(
                "포터",
                key="compare_pick_porter",
                use_container_width=True,
                type="primary" if selected_family == "포터" else "secondary",
                on_click=_set_family,
                args=("포터",),
            )

            def _show_detail():
                st.session_state.compare_show_detail = True
            
            st.button(
                "상세보기", 
                key="compare_next", 
                type="primary", 
                use_container_width=True,
                on_click=_show_detail,
            )

    with main_col:
        st.markdown('<div class="compare-page-spacer"></div>', unsafe_allow_html=True)

        # 위쪽: 일반(경유) 모델
        picked_top = _render_compare_card(
            key="compare_card_top",
            title="일반 (경유)",
            subtitle=f"{selected_family} 일반 모델",
            car_options=normal_cars,
            selected_name=st.session_state.compare_model_top,
        )
        st.session_state.compare_model_top = picked_top

        st.markdown('<div class="compare-divider"></div>', unsafe_allow_html=True)

        # 아래쪽: EV(전기) 모델
        picked_bottom = _render_compare_card(
            key="compare_card_bottom",
            title="EV (전기)",
            subtitle=f"{selected_family} EV 모델",
            car_options=ev_cars,
            selected_name=st.session_state.compare_model_bottom,
        )
        st.session_state.compare_model_bottom = picked_bottom