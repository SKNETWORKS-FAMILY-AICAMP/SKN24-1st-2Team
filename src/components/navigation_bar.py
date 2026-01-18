import streamlit as st

def render_navigation_bar():
  current_page = st.session_state.get('current_page', '통계 및 현황')
  menu_items = ["통계 및 현황", "차량 비교", "FAQ"]

  # 해당 메뉴 클릭 시 텍스트 색상 변경
  active_idx = menu_items.index(current_page) if current_page in menu_items else 0
  
  button_styles = ""
  for idx, item in enumerate(menu_items):
    if idx == active_idx:
      button_styles += f"""
        .st-key-nav_bar div[data-testid="stHorizontalBlock"] > div:nth-child({idx + 2}) button {{
          color: #ffffff !important;
        }}
      """
  
  st.markdown(f"<style>{button_styles}</style>", unsafe_allow_html=True)
  
  with st.container(key="nav_bar"):
    cols = st.columns([2] + [0.5] * len(menu_items) + [2])
    
    # 로고
    with cols[0]:
      st.markdown(
        '<p class="nav-logo">DumPs Up!</p>',
        unsafe_allow_html=True
      )
    
    # 메뉴
    for idx, item in enumerate(menu_items):
      with cols[idx + 1]:
        if st.button(item, key=f'nav_{item}', use_container_width=True):
          st.session_state.current_page = item
          st.rerun()
