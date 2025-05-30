import streamlit as st
import streamlit_shadcn_ui as ui
from components.auth import supabase_client, is_admin, logout

def admin_page():
    """관리자 페이지"""
    if not is_admin():
        st.error("관리자 권한이 필요합니다.")
        return
    
    st.title("🔧 관리자 패널")
    st.markdown("---")
    
    # 로그아웃 버튼
    col1, col2 = st.columns([6, 1])
    with col2:
        if ui.button("로그아웃", key="admin_logout"):
            success, message = logout()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    # 허용된 이메일 관리 섹션
    st.header("📧 허용된 이메일 관리")
    
    # 현재 허용된 이메일 목록 표시
    display_allowed_emails()
    
    st.markdown("---")
    
    # 새 이메일 추가 섹션
    add_email_section()
    
def display_allowed_emails():
    """허용된 이메일 목록 표시"""
    try:
        # Supabase MCP를 통해 허용된 이메일 목록 가져오기
        response = supabase_client.table('allowed_emails').select('*').order('created_at').execute()
        
        if response.data:
            st.subheader("현재 허용된 이메일 목록")
            
            # 헤더 표시
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1.5, 1])
            with col1:
                st.markdown("**📧 이메일**")
            with col2:
                st.markdown("**👤 이름**")
            with col3:
                st.markdown("**🏪 샵**")
            with col4:
                st.markdown("**📅 등록일**")
            with col5:
                st.markdown("**🗑️ 삭제**")
            
            st.markdown("---")
            
            # 데이터 표시
            for i, email_record in enumerate(response.data):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1.5, 1])
                
                with col1:
                    st.text(email_record['email'])
                
                with col2:
                    name = email_record.get('name', '') or '-'
                    st.text(name)
                
                with col3:
                    shop = email_record.get('shop', '') or '-'
                    st.text(shop)
                
                with col4:
                    st.text(email_record['created_at'][:10])  # 날짜만 표시
                
                with col5:
                    if ui.button("삭제", key=f"delete_{email_record['id']}"):
                        delete_email(email_record['id'], email_record['email'], 
                                   email_record.get('name'), email_record.get('shop'))
        else:
            st.info("현재 허용된 이메일이 없습니다.")
            
    except Exception as e:
        st.error(f"이메일 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

def add_email_section():
    """새 이메일 추가 섹션"""
    st.subheader("새 이메일 추가")
    
    with ui.card(key="add_email_card"):
        # 필수 필드
        st.markdown("**📧 이메일 (필수)**")
        new_email = ui.input(
            placeholder="example@domain.com",
            key="new_email_input"
        )
        
        # 선택 필드들
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 이름 (선택)**")
            new_name = ui.input(
                placeholder="홍길동",
                key="new_name_input"
            )
        
        with col2:
            st.markdown("**🏪 샵명 (선택)**")
            new_shop = ui.input(
                placeholder="바이오폭스 강남점",
                key="new_shop_input"
            )
        
        # 추가 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            if ui.button("추가", key="add_email_btn"):
                if new_email:
                    add_email(new_email, new_name, new_shop)
                else:
                    st.error("이메일을 입력해주세요.")

def add_email(email, name=None, shop=None):
    """새 이메일 추가"""
    try:
        # 이메일 형식 검증
        if '@' not in email or '.' not in email.split('@')[1]:
            st.error("올바른 이메일 형식을 입력해주세요.")
            return
        
        # 데이터 준비
        email_data = {
            'email': email.lower().strip()
        }
        
        # 선택 필드가 비어있지 않으면 추가
        if name and name.strip():
            email_data['name'] = name.strip()
        
        if shop and shop.strip():
            email_data['shop'] = shop.strip()
        
        # Supabase MCP를 통해 이메일 추가
        response = supabase_client.table('allowed_emails').insert(email_data).execute()
        
        if response.data:
            # 성공 메시지에 추가된 정보 표시
            success_msg = f"✅ {email} 이메일이 허용 목록에 추가되었습니다."
            if name and name.strip():
                success_msg += f" (이름: {name.strip()})"
            if shop and shop.strip():
                success_msg += f" (샵: {shop.strip()})"
            
            st.success(success_msg)
            # 입력 필드 초기화를 위해 페이지 새로고침
            st.rerun()
        else:
            st.error("이메일 추가에 실패했습니다.")
            
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg or "already exists" in error_msg:
            st.error("이미 존재하는 이메일입니다.")
        else:
            st.error(f"이메일 추가 중 오류가 발생했습니다: {error_msg}")

def delete_email(email_id, email, name=None, shop=None):
    """이메일 삭제"""
    try:
        # Supabase MCP를 통해 이메일 삭제
        response = supabase_client.table('allowed_emails').delete().eq('id', email_id).execute()
        
        if response.data:
            # 삭제 성공 메시지에 추가 정보 표시
            success_msg = f"✅ {email} 이메일이 허용 목록에서 삭제되었습니다."
            if name:
                success_msg += f" (이름: {name})"
            if shop:
                success_msg += f" (샵: {shop})"
            
            st.success(success_msg)
            st.rerun()
        else:
            st.error("이메일 삭제에 실패했습니다.")
            
    except Exception as e:
        st.error(f"이메일 삭제 중 오류가 발생했습니다: {str(e)}")

def get_allowed_emails_count():
    """허용된 이메일 개수 반환"""
    try:
        response = supabase_client.table('allowed_emails').select('id').execute()
        return len(response.data) if response.data else 0
    except:
        return 0