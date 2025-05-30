import streamlit as st
from datetime import datetime

def init_session_state():
    """세션 상태 초기화"""
    # 결과 저장을 위한 상태 초기화
    if 'result' not in st.session_state:
        st.session_state.result = None
    
    # 채팅 기능 활성화 상태
    if 'chat_enabled' not in st.session_state:
        st.session_state.chat_enabled = False
    
    # 채팅 메시지 기록
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 버전 관리
    if 'version_history' not in st.session_state:
        st.session_state.version_history = []
    
    # 폼 데이터 저장
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

def display_version(version):
    """특정 버전의 결과 표시"""
    if not 'version_history' in st.session_state or version < 1 or version > len(st.session_state.version_history):
        return
    
    # 선택한 버전의 데이터 표시
    version_data = st.session_state.version_history[version-1]['data']
    
    # 임시 표시용 상태 설정
    st.session_state.temp_display = {
        'version': version,
        'data': version_data
    }

def restore_version(version):
    """특정 버전으로 복원"""
    if not 'version_history' in st.session_state or version < 1 or version > len(st.session_state.version_history):
        return
    
    # 선택한 버전의 데이터로 복원
    version_data = st.session_state.version_history[version-1]['data']
    st.session_state.result = version_data.copy()
    
    # 새 버전으로 추가
    new_version = len(st.session_state.version_history) + 1
    st.session_state.version_history.append({
        'version': new_version,
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'data': version_data.copy()
    })
    
    st.success(f"버전 {version}에서 복원되었습니다.")
    st.rerun()
