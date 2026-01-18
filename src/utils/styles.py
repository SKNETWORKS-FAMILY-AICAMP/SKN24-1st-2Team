import streamlit as st
from pathlib import Path

"""
CSS 파일을 로드하여 스타일을 적용하기 위한 헬퍼 함수
"""
def load_css():
  if 'css_loaded' not in st.session_state:
    try:
      root_path = Path(__file__).parent.parent
      css_path = root_path / 'src' / 'assets' / 'styles.css'

      if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
          css = f.read()
        
        # css 적용
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

        st.session_state.css_loaded = True
        st.success('[STYLES] CSS 로드 성공')

    except Exception as e:
      st.error(f'[STYLES] CSS 로드 실패: {e}')
      st.session_state.css_loaded = False