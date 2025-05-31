import streamlit as st
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import os
from datetime import datetime

app = FastAPI()

class ResultNotification(BaseModel):
    job_id: str
    result: str = None
    result_data: dict = None
    status: str

# 결과 저장소 (메모리 기반 - 프로덕션에서는 Redis 사용 권장)
result_store = {}

@app.post("/api/result")
async def receive_result(notification: ResultNotification):
    """n8n에서 완료 알림을 받는 엔드포인트"""
    try:
        # 결과 저장
        result_store[notification.job_id] = {
            "status": notification.status,
            "result": notification.result,
            "result_data": notification.result_data,
            "received_at": datetime.now().isoformat()
        }
        
        print(f"✅ 결과 받음: {notification.job_id[:8]}... (상태: {notification.status})")
        
        return {
            "success": True,
            "message": f"결과를 성공적으로 받았습니다. job_id: {notification.job_id[:8]}...",
            "received_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 결과 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """결과 조회 엔드포인트"""
    if job_id in result_store:
        return result_store[job_id]
    else:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")

@app.get("/api/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 개발용 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)