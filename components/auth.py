import streamlit as st
import streamlit_shadcn_ui as ui
import supabase

# Supabase 클라이언트 설정
SUPABASE_URL = "https://bbkwmpygoxveuzppcfsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJia3dtcHlnb3h2ZXV6cHBjZnNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzNDQ1MTUsImV4cCI6MjA2MzkyMDUxNX0.D-R55xaWMBZp5gg8IwG2BkRgI6JjdKjbc5vnul4mfcY"

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def init_auth_session():
    """세션 상태 초기화 및 자동 로그인 복원"""
    # 입력 필드 초기화를 위한 플래그 설정
    if 'init_done' not in st.session_state:
        # 처음 실행 시 입력 필드 초기화
        for key in ['login_email', 'login_password', 'signup_email', 'signup_password', 'signup_password_confirm']:
            st.session_state[key] = ""
        st.session_state.init_done = True
    
    # 기본 세션 상태 초기화
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'remember_login' not in st.session_state:
        st.session_state.remember_login = True  # 기본값을 True로 설정
    
    # 현재 Supabase 세션 가져오기 시도
    try:
        # Supabase에서 세션 가져오기 시도
        session = supabase_client.auth.get_session()
        
        if session and session.access_token:
            # 세션이 있으면 사용자 정보 가져오기
            try:
                user_response = supabase_client.auth.get_user(session.access_token)
                if user_response and user_response.user:
                    # 세션 자동 복원
                    st.session_state.user = user_response.user
                    st.session_state.token = session.access_token
                    st.session_state.authenticated = True
                    # 로그인 유지 상태를 True로 유지
                    st.session_state.remember_login = True
                    return
            except Exception as e:
                # 토큰이 유효하지 않은 경우 조용히 처리
                st.session_state.user = None
                st.session_state.token = None
                st.session_state.authenticated = False
    except Exception as e:
        # 오류 발생 시 세션 초기화 (조용히 오류 처리)
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.authenticated = False

def login(email, password, remember=False):
    """사용자 로그인 처리"""
    try:
        # 7일 동안 세션 유지
        # Supabase의 기본 세션 유효 기간은 약 1시간
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
            
        user = response.user
        session = response.session
        
        if user and session:
            # 사용자 정보 및 토큰 저장
            st.session_state.user = user
            st.session_state.token = session.access_token
            st.session_state.authenticated = True
            
            # 세션 유지 설정
            st.session_state.remember_login = remember
            
            # 항상 supabase 세션 설정 (로그인 유지 여부와 상관없이)
            supabase_client.auth.set_session(session.access_token, session.refresh_token)
            
            # 로그인 성공 후 입력란 초기화 플래그 설정
            st.session_state.login_form_reset = True
            
            return True, "로그인 성공"
        else:
            return False, "로그인 실패"
    except Exception as e:
        return False, f"로그인 오류: {str(e)}"

def signup(email, password):
    """회원가입 처리"""
    try:
        # 먼저 허용된 이메일인지 확인
        allowed_check = supabase_client.table('allowed_emails').select('email').eq('email', email).execute()
        
        if not allowed_check.data:
            return False, "이 이메일 주소는 가입이 허용되지 않습니다. 관리자에게 문의하세요."
        
        response = supabase_client.auth.sign_up({"email": email, "password": password})
        if response.user:
            return True, "회원가입 성공! 이메일을 확인해주세요."
        else:
            return False, "회원가입 실패"
    except Exception as e:
        # 데이터베이스 트리거에서 발생한 오류 메시지 처리
        error_msg = str(e)
        if "Registration not allowed" in error_msg:
            return False, "이 이메일 주소는 가입이 허용되지 않습니다. 관리자에게 문의하세요."
        return False, f"회원가입 오류: {error_msg}"

def logout():
    """로그아웃 처리"""
    try:
        supabase_client.auth.sign_out()
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.authenticated = False
        # remember_login 상태도 초기화
        st.session_state.remember_login = False
        # 로그아웃 시 입력란 초기화 플래그 설정
        st.session_state.login_form_reset = True
        st.session_state.signup_form_reset = True
        return True, "로그아웃 되었습니다."
    except Exception as e:
        return False, f"로그아웃 오류: {str(e)}"

def is_authenticated():
    """인증 상태 확인"""
    # 세션에서 토큰이 있는지 확인
    if st.session_state.authenticated and st.session_state.token:
        try:
            # 토큰 유효성 검증
            response = supabase_client.auth.get_user(st.session_state.token)
            if response.user:
                return True
        except:
            # 토큰이 유효하지 않으면 인증 상태 초기화
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.token = None
    return False

def is_admin():
    """관리자 권한 확인"""
    if not is_authenticated():
        return False
    
    # 현재 로그인한 사용자가 admin@biofox.com인지 확인
    if st.session_state.user and st.session_state.user.email == 'admin@biofox.com':
        return True
    return False

def auth_required(func):
    """인증이 필요한 페이지에 데코레이터로 사용"""
    def wrapper(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            st.warning("이 페이지를 보려면 로그인이 필요합니다.")
            login_page()
            return None
    return wrapper

def login_page():
    """로그인 페이지 UI"""
    init_auth_session()
    
    if is_authenticated():
        st.success("이미 로그인되어 있습니다.")
        if ui.button("로그아웃", key="logout_button"):
            success, message = logout()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        return True
    
    # 페이지 로드 시 입력창 초기화를 위한 코드
    # 세션 상태에 대한 참조를 제거하고 매번 반드시 빈 문자열로 초기화
    for field in ['login_email', 'login_password']:
        if field in st.session_state:
            del st.session_state[field]
    
    for field in ['signup_email', 'signup_password', 'signup_password_confirm']:
        if field in st.session_state:
            del st.session_state[field]
    
    with ui.card(key="login_card"):
        st.title("로그인")
        
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            # 새로운 입력창 생성 - 레이블 숨김
            st.markdown("<p style='font-size:0.9em; margin-bottom:5px;'>이메일</p>", unsafe_allow_html=True)
            email = ui.input("", placeholder="example@email.com", key="login_email_new")
            
            st.markdown("<p style='font-size:0.9em; margin-bottom:5px;'>비밀번호</p>", unsafe_allow_html=True)
            password = ui.input("", placeholder="비밀번호", type="password", key="login_password_new")
            
            remember = ui.checkbox(label="7일 동안 로그인 유지", key="remember_me")
            
            if ui.button("로그인", key="login_button"):
                if not email or not password:
                    st.error("이메일과 비밀번호를 모두 입력해주세요.")
                else:
                    success, message = login(email, password, remember)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            # 새로운 입력창 생성 - 레이블 숨김
            st.markdown("<p style='font-size:0.9em; margin-bottom:5px;'>이메일</p>", unsafe_allow_html=True)
            email = ui.input("", placeholder="example@email.com", key="signup_email_new")
            
            st.markdown("<p style='font-size:0.9em; margin-bottom:5px;'>비밀번호</p>", unsafe_allow_html=True)
            password = ui.input("", placeholder="비밀번호", type="password", key="signup_password_new")
            
            st.markdown("<p style='font-size:0.9em; margin-bottom:5px;'>비밀번호 확인</p>", unsafe_allow_html=True)
            password_confirm = ui.input("", placeholder="비밀번호 확인", type="password", key="signup_password_confirm_new")
            
            if ui.button("회원가입", key="signup_button"):
                if not email or not password:
                    st.error("이메일과 비밀번호를 모두 입력해주세요.")
                elif password != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    success, message = signup(email, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
