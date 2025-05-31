#!/usr/bin/env python3
"""
BIOFOX 자동화 서버 시작 스크립트
- FastAPI 서버 (포트 8001)
- Streamlit 앱 (포트 8501)
"""

import subprocess
import time
import sys
import os

def start_fastapi():
    """FastAPI 서버 시작"""
    print("🚀 FastAPI 서버 시작 중... (포트 8001)")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "api:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ])

def start_streamlit():
    """Streamlit 앱 시작"""
    print("🎨 Streamlit 앱 시작 중... (포트 8501)")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", 
        "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

def main():
    print("=" * 50)
    print("🦊 BIOFOX 자동화 시스템 시작")
    print("=" * 50)
    
    try:
        # FastAPI 서버 시작
        fastapi_process = start_fastapi()
        time.sleep(2)  # FastAPI 시작 대기
        
        # Streamlit 앱 시작
        streamlit_process = start_streamlit()
        time.sleep(2)  # Streamlit 시작 대기
        
        print("✅ 모든 서버가 시작되었습니다!")
        print("📊 FastAPI API: http://localhost:8001")
        print("🎨 Streamlit 앱: http://localhost:8501")
        print("📋 API 문서: http://localhost:8001/docs")
        print("\n종료하려면 Ctrl+C를 누르세요...")
        
        # 프로세스 모니터링
        while True:
            time.sleep(1)
            
            # 프로세스 상태 확인
            if fastapi_process.poll() is not None:
                print("❌ FastAPI 서버가 종료되었습니다.")
                break
                
            if streamlit_process.poll() is not None:
                print("❌ Streamlit 앱이 종료되었습니다.")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 서버 종료 중...")
        
        # 프로세스 종료
        if 'fastapi_process' in locals():
            fastapi_process.terminate()
        if 'streamlit_process' in locals():
            streamlit_process.terminate()
            
        print("✅ 모든 서버가 종료되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()