import streamlit as st
from src.utils.styles import load_css
from src.components.navigation_bar import render_navigation_bar

load_css()

st.set_page_config(
  page_title='DumPs Up!',
  layout='wide',
  initial_sidebar_state='collapsed',
)

if 'current_page' not in st.session_state:
  st.session_state.current_page = '통계 및 현황'

render_navigation_bar()

# 페이지 라우팅
from pathlib import Path
import sys

root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

if st.session_state.current_page == '통계 및 현황':
  statistics_path = root_path / 'pages' / 'statistics.py'
  if statistics_path.exists():
    with open(statistics_path, 'r', encoding='utf-8') as f:
      code = f.read()
      exec(code)
  else:
    st.info('통계 및 현황 페이지를 준비 중입니다.')

elif st.session_state.current_page == '차량 비교':
  compare_path = root_path / 'pages' / 'compare.py'
  if compare_path.exists():
    with open(compare_path, 'r', encoding='utf-8') as f:
      code = f.read()
      exec(code)
  else:
    st.info('차량 비교 페이지를 준비 중입니다.')
    
elif st.session_state.current_page == 'FAQ':
  with open(root_path / 'pages' / 'faq.py', 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code)