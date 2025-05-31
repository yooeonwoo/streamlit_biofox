import streamlit as st
import streamlit_shadcn_ui as ui
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 컴포넌트 도입
from components.webhook import call_n8n_webhook_async, check_job_result
from components.ui import show_input_form, show_results, init_page
from components.session import init_session_state, display_version, restore_version
from components.auth import login_page, auth_required, is_authenticated, init_auth_session, is_admin
from components.admin import admin_page

# 환경 변수 로드
load_dotenv()

def generate_content(form_data):
    """광고 컨텐츠 생성 - 비동기 방식"""
    # 컨텐츠 타입에 따른 예상 시간 안내
    platform = form_data.get('platform', '인스타그램')
    if platform == '블로그':
        time_msg = "✨ 블로그 포스트를 생성하고 있습니다... (예상 소요시간: 최대 3분)"
    else:
        time_msg = "✨ 인스타그램 광고를 생성하고 있습니다... (예상 소요시간: 약 1분 30초)"
    
    # 진행 상태 표시
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    with progress_placeholder:
        st.info(time_msg)
    
    try:
        # 비동기 웹훅 API 호출 (클라이언트 job_id 생성)
        job_id = call_n8n_webhook_async({
            "type": "generate",
            "data": form_data
        })
        
        if job_id:
            # 세션 상태 업데이트
            st.session_state.current_job_id = job_id
            st.session_state.job_status = "processing"
            st.session_state.form_data = form_data
            return True
        else:
            with status_placeholder:
                st.error("❌ 요청 처리 중 오류가 발생했습니다.")
            return False
            
    except Exception as e:
        with status_placeholder:
            st.error(f"❌ 오류 발생: {str(e)}")
        return False
    finally:
        # 진행 상태 표시 제거
        progress_placeholder.empty()
        status_placeholder.empty()

def handle_chat_input(user_input):
    """채팅 입력 처리"""
    # 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 수정 요청
    # 현재 컨텐츠 타입 확인
    current_content = st.session_state.get('result', {})
    has_blog_content = bool(current_content.get('blog_content') or current_content.get('blog_title'))
    
    if has_blog_content:
        modify_msg = "✏️ 블로그 포스트를 수정하고 있습니다... (예상 소요시간: 최대 3분)"
    else:
        modify_msg = "✏️ 인스타그램 광고를 수정하고 있습니다... (예상 소요시간: 약 1분 30초)"
    
    # 진행 상태 표시
    progress_placeholder = st.empty()
    with progress_placeholder:
        st.info(modify_msg)
    
    # 전체 수정 히스토리 구성
    modification_history = []
    for version in st.session_state.get('version_history', []):
        modification_history.append({
            "version": version['version'],
            "timestamp": version['timestamp'],
            "content": version['data'],
            "user_request": version.get('user_request'),
            "is_original": version.get('is_original', False)
        })
    
    # 원본 콘텐츠 찾기 (첫 번째 버전)
    original_content = None
    if modification_history and modification_history[0].get('is_original'):
        original_content = modification_history[0]['content']
    
    modify_data = {
        "type": "modify",
        "is_modification": True,  # 수정 요청임을 명시하는 플래그
        "data": {
            "current_request": user_input,  # 현재 수정 요청
            "modification_request": user_input,  # 수정 요청 내용 (명확한 변수명)
            
            # 전체 히스토리 정보
            "modification_history": modification_history,  # 전체 수정 히스토리
            "original_content": original_content,  # 맨 처음 원본
            "current_content": st.session_state.result,  # 현재 결과
            
            # 기존 호환성 유지
            "original_result": st.session_state.result,  # 이전 출력 결과
            "previous_output": {
                "headline": st.session_state.result.get('headline', ''),
                "caption": st.session_state.result.get('caption', ''),
                "hashtags": st.session_state.result.get('hashtags', []),
                "blog_title": st.session_state.result.get('blog_title', ''),
                "blog_content": st.session_state.result.get('blog_content', '')
            },
            "user_request": user_input,  # 사용자의 수정 요청
            "context": st.session_state.get('form_data', {}),  # 원본 폼 데이터
            "version_history": st.session_state.get('version_history', [])  # 버전 히스토리
        }
    }
    
    result = call_n8n_webhook_async(modify_data, webhook_type="modify")
    
    # 진행 상태 표시 제거
    progress_placeholder.empty()
    
    if result and result.get('status') == 'success':
        # 수정된 결과 업데이트
        modified_data = result['data']
        
        # 결과 업데이트
        if 'modified_headline' in modified_data:
            st.session_state.result['headline'] = modified_data['modified_headline']
        if 'modified_caption' in modified_data:
            st.session_state.result['caption'] = modified_data['modified_caption']
        if 'modified_hashtags' in modified_data:
            st.session_state.result['hashtags'] = modified_data['modified_hashtags']
        
        # 응답 메시지 추가
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "✅ 수정이 완료되었습니다."
        })
        
        # 버전 기록 업데이트
        new_version = len(st.session_state.version_history) + 1
        st.session_state.version_history.append({
            'version': new_version,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'data': st.session_state.result.copy(),
            'user_request': user_input,  # 이번 수정 요청 저장
            'is_original': False  # 수정본임을 표시
        })
        return True
    else:
        # 오류 메시지 추가
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "❌ 수정 중 오류가 발생했습니다. 다시 시도해주세요."
        })
        return False

def main():
    """메인 앱 함수"""
    # 페이지 설정
    init_page()
    
    # 세션 상태 초기화
    init_session_state()
    
    # 인증 세션 초기화
    init_auth_session()
    
    # 앱 제목
    st.title("✨ BIOFOX 자동화")
    
    # 로그인 상태 확인
    if not is_authenticated():
        login_page()
        return
    
    # 관리자 권한 확인 - 관리자면 관리자 페이지만 표시
    if is_admin():
        admin_page()
        return
    
    # 작업 상태 확인 
    if 'current_job_id' in st.session_state and st.session_state.get('job_status') == 'processing':
        job_id = st.session_state.current_job_id
        
        # 수동 확인 버튼 추가
        if st.button("🔄 수동으로 결과 확인"):
            st.session_state.job_status = "processing"  # 강제 리셋
            st.rerun()
        
        # 상태 UI 표시
        st.info(f"🔄 콘텐츠 생성 중입니다... 잠시만 기다려주세요. (작업 ID: {job_id[:8]}...)")
        
        # 결과 확인
        result = check_job_result(job_id)
        
        if result:
            # 결과 저장 및 상태 업데이트
            st.session_state.result = result
            st.session_state.job_status = "completed"
            
            # 버전 관리용 히스토리 추가
            st.session_state.version_history = [{
                'version': 1,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'data': result.copy(),
                'is_original': True
            }]
            
            # 페이지 리로드
            st.rerun()
        else:
            # 결과가 아직 없으면 자동 새로고침
            st.markdown("""
            <script>
                // 5초 후 자동 새로고침
                setTimeout(function() {
                    window.location.reload();
                }, 5000);
            </script>
            """, unsafe_allow_html=True)
    
    # 임시 표시 상태 확인 (버전 미리보기)
    elif 'temp_display' in st.session_state and st.session_state.temp_display:
        version_data = st.session_state.temp_display
        
        st.info(f"버전 {version_data['version']} 미리보기")
        
        # 데이터 표시
        if 'headline' in version_data['data']:
            st.markdown("### 📣 광고 헤드라인")
            st.code(version_data['data']['headline'])
        
        if 'caption' in version_data['data']:
            st.markdown("### 📱 인스타그램 캡션")
            st.code(version_data['data']['caption'])
        
        if 'hashtags' in version_data['data']:
            st.markdown("### 🏷️ 해시태그")
            st.code(' '.join(version_data['data']['hashtags']))
        
        # 닫기 버튼
        close_btn = ui.button(text="닫기")
        if close_btn:
            st.session_state.temp_display = None
            st.rerun()
    else:
        # 결과가 없으면 입력 폼 표시
        if not st.session_state.get('result'):
            form_data = show_input_form()
            if form_data:
                if generate_content(form_data):
                    st.rerun()
        else:
            show_results()

if __name__ == "__main__":
    main()
