import streamlit as st
from pathlib import Path

"""
CSS 파일을 로드하여 스타일을 적용하기 위한 헬퍼 함수
"""
def load_css():
  try:
    src_path = Path(__file__).parent.parent
    css_path = src_path / 'assets' / 'styles.css'

    if css_path.exists():
      with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()
      
      # CSS 적용
      st.markdown(
        f'<style>{css}</style>',
        unsafe_allow_html=True
      )

  except Exception as e:
    st.error(f'[STYLES] CSS 로드 실패: {e}')