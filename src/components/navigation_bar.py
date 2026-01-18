import streamlit as st
from src.utils.styles import load_css

def render_navigation_bar():
  load_css()
  
  st.markdown("""
    <div class="nav-bar-container">
      <nav class="nav-bar">
  """, unsafe_allow_html=True)
  
  logo, links = st.columns([1, 2])

  with logo:
    st.markdown('<div class="logo">DumPs Up!</div>', unsafe_allow_html=True)
  
  with links:
    menu_items = [
      "통계 및 현황",
      "차량 비교",
      "FAQ",
    ]

    cols = st.columns(len(menu_items))
    for idx, (col, item) in enumerate(zip(cols, menu_items)):
      with col:
        is_active = (st.session_state.get('current_page', '통계 및 현황') == item)
        active_class = 'active' if is_active else ''
        if st.button(item, key=f'nav_{item}', use_container_width=True):
          st.session_state.current_page = item
          st.rerun()

  st.markdown("""
      </nav>
    </div>
  """, unsafe_allow_html=True)
    