import os
import uuid
import json
from supabase import create_client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 생성
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def create_job(data):
    """새 작업 생성 및 job_id 반환"""
    job_id = str(uuid.uuid4())
    
    try:
        supabase.table("job_status").insert({
            "job_id": job_id,
            "status": "pending",
            "request_data": data
        }).execute()
        return job_id
    except Exception as e:
        print(f"작업 생성 오류: {str(e)}")
        return None

def get_job_status(job_id):
    """작업 상태 확인"""
    try:
        response = supabase.table("job_status").select("*").eq("job_id", job_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"작업 상태 확인 오류: {str(e)}")
        return None

def get_job_result(job_id):
    """작업 결과 확인"""
    try:
        import streamlit as st
        from supabase import create_client
        import os
        
        # 새로운 Supabase 클라이언트 생성 (캐싱 이슈 방지)
        fresh_supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # 최신 데이터 조회
        all_response = fresh_supabase.table("job_status").select("*").eq("job_id", job_id).execute()
        st.info(f"🔍 job_id {job_id[:8]}...로 검색한 결과: {len(all_response.data)}개")
        
        if all_response.data:
            record = all_response.data[0]
            st.info(f"📊 실시간 레코드 상태: {record.get('status')} (완료시간: {record.get('completed_at')})")
            
            # completed 상태인지 확인
            if record.get('status') == 'completed':
                st.success("✅ 완료된 작업을 찾았습니다!")
                st.info(f"📄 result 크기: {len(str(record.get('result', '')))}")
                st.info(f"📊 result_data 타입: {type(record.get('result_data'))}")
                return record
            else:
                st.warning(f"⏳ 작업이 아직 {record.get('status')} 상태입니다.")
                # 강제로 다시 새로고침 (더 자주)
                st.markdown("""
                <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 3000);
                </script>
                """, unsafe_allow_html=True)
                return None
        else:
            st.error("❌ 해당 job_id를 찾을 수 없습니다.")
            return None
            
    except Exception as e:
        import streamlit as st
        st.error(f"작업 결과 확인 오류: {str(e)}")
        return None