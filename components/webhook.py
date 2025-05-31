import requests
import os
import json
import re
import uuid
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from components.supabase_client import get_job_result

def parse_blog_format(content):
    """블로그 형식 파싱 ([제목], [3줄 요약], [본문], [태그] 구조)
    
    Args:
        content (str): 파싱할 블로그 텍스트 콘텐츠
    
    Returns:
        dict: 파싱된 블로그 데이터
    """
    try:
        result = {
            "headline": "",
            "caption": "",
            "hashtags": [],
            "blog_title": "",
            "blog_content": ""
        }
        
        # [제목] 섹션 추출
        title_match = re.search(r'\[제목\]\s*\n(.*?)(?=\n\[|$)', content, re.DOTALL)
        if title_match:
            blog_title = title_match.group(1).strip()
            result["blog_title"] = blog_title
            # 블로그에서는 headline을 비워둠 (블로그 타이틀만 사용)
        
        # [3줄 요약] + [본문] 섹션 합쳐서 추출
        summary_match = re.search(r'\[3줄 요약\]\s*\n(.*?)(?=\n\[본문\])', content, re.DOTALL)
        # [본문] 섹션 추출 - 각주 제외하고 추출
        content_match = re.search(r'\[본문\]\s*\n(.*?)(?=\n\[태그\]|------|\n\n※|$)', content, re.DOTALL)
        
        blog_content_parts = []
        if summary_match:
            blog_content_parts.append(summary_match.group(1).strip())
        if content_match:
            blog_content_parts.append(content_match.group(1).strip())
        
        # [본문]만 있는 경우도 처리 (3줄 요약이 없는 경우)
        if not blog_content_parts and not summary_match:
            content_only_match = re.search(r'\[본문\]\s*\n(.*?)(?=------|\n\n※|$)', content, re.DOTALL)
            if content_only_match:
                blog_content_parts.append(content_only_match.group(1).strip())
            
        if blog_content_parts:
            blog_content = "\n\n".join(blog_content_parts)
            result["blog_content"] = blog_content
            result["caption"] = blog_content  # 인스타그램용으로도 사용
            st.info(f"📄 블로그 본문 길이: {len(blog_content)}")
        
        # [태그] 섹션 추출 - 블로그에는 태그 섹션이 없을 수도 있음
        tag_match = re.search(r'\[태그\]\s*\n(.*?)(?=\n\[|------|\n\n※|$)', content, re.DOTALL)
        if tag_match:
            tag_text = tag_match.group(1).strip()
            if tag_text:
                hashtags = tag_text.replace('\n', ' ').split()
                # 빈 문자열 제거 및 # 확인
                result["hashtags"] = [tag for tag in hashtags if tag.strip() and tag.startswith('#')]
        else:
            # 태그 섹션이 없으면 빈 배열
            result["hashtags"] = []
        
        # 각주 섹션 추출 - 블로그에는 각주가 없을 수도 있음
        footnote_match = re.search(r'------\s*\n(※.*?)$', content, re.DOTALL)
        if footnote_match:
            footnote_text = footnote_match.group(1).strip()
            if footnote_text:
                # 각주 중복 확인 - 천방케어 키워드로 체크 (가장 확실한 방법)
                has_footnote_in_blog = result["blog_content"] and "천방케어는 MICROJET" in result["blog_content"]
                has_footnote_in_caption = result["caption"] and "천방케어는 MICROJET" in result["caption"]
                
                # 블로그 콘텐츠에 각주가 이미 포함되어 있지 않은 경우에만 추가
                if result["blog_content"] and not has_footnote_in_blog:
                    result["blog_content"] += f"\n\n{footnote_text}"
                if result["caption"] and not has_footnote_in_caption:
                    result["caption"] += f"\n\n{footnote_text}"
        
        return result
        
    except Exception as e:
        st.error(f"블로그 형식 파싱 오류: {str(e)}")
        # 오류 발생 시 빈 결과 반환
        return {
            "headline": "",
            "caption": "",
            "hashtags": [],
            "blog_title": "",
            "blog_content": ""
        }

def parse_instagram_format(content):
    """새로운 텍스트 형식 파싱 ([후킹문구], [캡션], [해시태그] 구조)
    
    Args:
        content (str): 파싱할 텍스트 콘텐츠
    
    Returns:
        dict: 파싱된 광고 데이터
    """
    try:
        result = {
            "headline": "",
            "caption": "",
            "hashtags": [],
            "blog_title": "",
            "blog_content": ""
        }
        
        # [후킹문구] 섹션 추출
        hook_match = re.search(r'\[후킹문구\]\s*\n(.*?)(?=\n\[|$)', content, re.DOTALL)
        if hook_match:
            result["headline"] = hook_match.group(1).strip()
        
        # [캡션] 섹션 추출 - 각주 제외하고 추출
        caption_match = re.search(r'\[캡션\]\s*\n(.*?)(?=\n\[|------|\n\n※)', content, re.DOTALL)
        if caption_match:
            caption_text = caption_match.group(1).strip()
            result["caption"] = caption_text
            # 블로그용으로도 사용
            result["blog_content"] = caption_text
            result["blog_title"] = result["headline"]  # 후킹문구를 블로그 제목으로 사용
            
        # 각주 섹션 추출 (------ 이후의 모든 ※ 내용들)
        footnote_match = re.search(r'------\s*\n(※.*?)$', content, re.DOTALL)
        if footnote_match:
            footnote_text = footnote_match.group(1).strip()
            if footnote_text:
                # 각주 중복 확인 - 천방케어 키워드로 체크 (가장 확실한 방법)
                has_footnote_in_caption = result["caption"] and "천방케어는 MICROJET" in result["caption"]
                has_footnote_in_blog = result["blog_content"] and "천방케어는 MICROJET" in result["blog_content"]
                
                # 캡션과 블로그 콘텐츠에 각주가 이미 포함되어 있지 않은 경우에만 추가
                if result["caption"] and not has_footnote_in_caption:
                    result["caption"] += f"\n\n{footnote_text}"
                if result["blog_content"] and not has_footnote_in_blog:
                    result["blog_content"] += f"\n\n{footnote_text}"
        
        # [해시태그] 섹션 추출
        hashtag_match = re.search(r'\[해시태그\]\s*\n(.*?)(?=\n\[|------|\n\n※|$)', content, re.DOTALL)
        if hashtag_match:
            hashtag_text = hashtag_match.group(1).strip()
            # 해시태그를 공백으로 분리하여 배열로 변환
            if hashtag_text:
                hashtags = hashtag_text.replace('\n', ' ').split()
                # 빈 문자열 제거 및 # 확인
                result["hashtags"] = [tag for tag in hashtags if tag.strip() and tag.startswith('#')]
        
        return result
        
    except Exception as e:
        st.error(f"새로운 텍스트 형식 파싱 오류: {str(e)}")
        # 오류 발생 시 빈 결과 반환
        return {
            "headline": "",
            "caption": "",
            "hashtags": [],
            "blog_title": "",
            "blog_content": ""
        }

# 환경변수 강제 재로드
load_dotenv(override=True)

def call_n8n_webhook_async(data, webhook_type="generate"):
    """클라이언트에서 job_id 생성 후 n8n에 즉시 응답 요청"""
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if not webhook_url:
        st.error(f"❌ 웹훅 URL이 설정되지 않았습니다. ({webhook_type})")
        return None
    
    try:
        # 클라이언트에서 job_id 생성
        job_id = str(uuid.uuid4())
        
        # 요청 데이터에 job_id 포함
        request_data = {
            "job_id": job_id,  # 클라이언트에서 생성한 job_id
            **data
        }
        
        # 기본 요청 설정
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BIOFOX-AdGenerator/1.0'
        }
        
        st.info(f"🚀 요청 시작: {datetime.now().strftime('%H:%M:%S')} (작업 ID: {job_id[:8]}...)")
        
        # 요청 전송 - 즉시 응답 기대
        response = requests.post(
            webhook_url,
            json=request_data,
            headers=headers,
            timeout=30  # 즉시 응답만 기다림
        )
        
        # 응답 확인 (200 또는 202 모두 허용)
        if response.status_code in [200, 202]:
            try:
                json_data = response.json()
                # n8n이 즉시 응답하면 202, Respond to Webhook 없으면 200
                if json_data.get('status') == 'processing' or response.status_code == 202:
                    st.success(f"✅ 요청이 접수되었습니다. 작업 ID: {job_id[:8]}...")
                    # 세션에 job_id 저장
                    st.session_state.current_job_id = job_id
                    st.session_state.job_status = "processing"
                    return job_id
                elif response.status_code == 200:
                    # n8n이 바로 200으로 응답한 경우도 허용
                    st.success(f"✅ 요청이 접수되었습니다. 작업 ID: {job_id[:8]}...")
                    st.session_state.current_job_id = job_id
                    st.session_state.job_status = "processing"
                    return job_id
                else:
                    st.error("❌ 예상하지 못한 응답입니다.")
                    st.code(f"응답: {json_data}")
                    return None
            except Exception as e:
                st.error(f"❌ 응답 처리 중 오류: {str(e)}")
                st.code(f"응답 텍스트: {response.text}")
                return None
        else:
            st.error(f"❌ 웹훅 호출 오류: {response.status_code}")
            st.code(f"응답: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ 웹훅 호출 중 예외 발생: {str(e)}")
        return None

def check_job_result_from_api(job_id):
    """API에서 작업 결과 확인 (POST 방식)"""
    try:
        # 로컬 API 서버에서 결과 확인
        import requests
        
        api_url = f"http://localhost:8001/api/result/{job_id}"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            result_data = response.json()
            st.success(f"✅ API에서 결과를 찾았습니다! (수신 시간: {result_data.get('received_at', '')})")
            
            # 결과 파싱
            if result_data.get('result_data'):
                return process_llm_response(result_data['result_data'])
            elif result_data.get('result'):
                return process_llm_response({"content": result_data['result']})
            else:
                st.error("❌ 결과 데이터가 없습니다.")
                return None
                
        elif response.status_code == 404:
            st.warning("⏳ 아직 결과가 없습니다...")
            return None
        else:
            st.error(f"❌ API 호출 오류: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ API 서버에 연결할 수 없습니다. Supabase로 대체 확인...")
        # Supabase 백업 방식
        return check_job_result_from_supabase(job_id)
    except Exception as e:
        st.error(f"❌ API 결과 확인 오류: {str(e)}")
        return None

def check_job_result_from_supabase(job_id):
    """Supabase에서 작업 결과 확인 (백업 방식)"""
    result = get_job_result(job_id)
    if not result:
        return None
    
    # 결과 파싱
    try:
        if isinstance(result.get('result_data'), str):
            result_data = json.loads(result.get('result_data', '{}'))
        else:
            result_data = result.get('result_data', {})
            
        if not result_data and result.get('result'):
            return process_llm_response({"content": result.get('result')})
            
        return process_llm_response(result_data)
    except Exception as e:
        st.error(f"❌ 결과 처리 중 오류: {str(e)}")
        return None

# 기본값을 API 방식으로 설정
def check_job_result(job_id):
    """작업 결과 확인 (API 우선, Supabase 백업)"""
    return check_job_result_from_api(job_id)


def process_llm_response(response_data):
    """웹훅 응답을 파싱하여 응용 프로그램에 맞는 형식으로 변환
    
    Args:
        response_data (dict or list): 웹훅 응답 데이터
    
    Returns:
        dict: 파싱된 광고 데이터 (헤드라인, 캡션, 해시태그, 블로그 제목, 블로그 내용)
    """
    try:
        st.info(f"🔍 응답 데이터 타입: {type(response_data)}")
        
        # 응답이 리스트인 경우 첫 번째 항목 사용
        if isinstance(response_data, list) and len(response_data) > 0:
            st.info(f"📋 리스트 응답, 첫 번째 항목 사용")
            response_data = response_data[0]
        
        st.info(f"🔍 처리 데이터 키: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not dict'}")
        
        # 1. 응답에서 콘텐츠 추출
        content = None
        if 'output' in response_data:
            content = response_data['output']
            st.info(f"📝 output 필드 발견, 길이: {len(content) if content else 0}")
            
            # 새로운 텍스트 형식 파싱 
            if content and isinstance(content, str):
                # 블로그 형식인지 확인 ([제목], [3줄 요약], [본문], [태그])
                if '[제목]' in content and '[본문]' in content:
                    st.info("📚 블로그 형식으로 파싱")
                    return parse_blog_format(content)
                # 인스타그램 형식 ([후킹문구], [캡션], [해시태그])
                elif '[후킹문구]' in content and '[캡션]' in content:
                    st.info("📱 인스타그램 형식으로 파싱")
                    return parse_instagram_format(content)
                # 일반 텍스트 처리
                else:
                    st.info("📄 기본 인스타그램 형식으로 파싱")
                    return parse_instagram_format(content)  # 기본값으로 인스타그램 파싱
                
        # JSON 형태의 응답 직접 파싱 시도 (기존 호환성)
        if content and isinstance(content, str):
            try:
                # 바로 JSON 파싱 시도
                parsed_data = json.loads(content)
                
                # 해시태그 문자열을 배열로 변환
                if 'hashtags' in parsed_data and isinstance(parsed_data['hashtags'], str):
                    hashtags_text = parsed_data['hashtags'].strip()
                    if hashtags_text:
                        # 공백으로 분리하여 배열로 만들기
                        parsed_data['hashtags'] = hashtags_text.split()
                
                return parsed_data
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 계속 진행
                pass
                
                # json{ 형태의 응답 처리 (백업)
                if content.startswith('json{'):
                    try:
                        # json{ 접두어 제거하고 JSON 파싱 시도
                        json_content = content[4:].strip()
                        parsed_data = json.loads(json_content)
                        
                        # 해시태그 문자열을 배열로 변환
                        if 'hashtags' in parsed_data and isinstance(parsed_data['hashtags'], str):
                            hashtags_text = parsed_data['hashtags'].strip()
                            if hashtags_text:
                                parsed_data['hashtags'] = hashtags_text.split()
                        
                        return parsed_data
                    except json.JSONDecodeError:
                        # 파싱 실패 시 계속 진행
                        pass
        elif 'content' in response_data:
            content = response_data['content']
        elif 'data' in response_data and isinstance(response_data['data'], dict):
            # API 응답이 data 키에 내용을 포함하는 경우
            return response_data['data']
        
        # 콘텐츠가 없는 경우 빈 결과 반환
        if not content:
            return {"headline": "", "caption": "", "hashtags": [], "blog_title": "", "blog_content": ""}
        
        # 2. 기본 결과 객체 초기화
        result = {}
        
        # 3. JSON 콘텐츠 추출 시도 (```json ... ```)
        json_match = re.search(r'```json\s*\n(.+?)\n```', content, re.DOTALL)
        if json_match:
            try:
                # JSON 파싱 시도
                json_content = json_match.group(1).strip()
                parsed_json = json.loads(json_content)
                
                # 파싱된 JSON에서 필드 추출
                for field in ['headline', 'blog_title', 'caption', 'blog_content']:
                    if field in parsed_json:
                        result[field] = parsed_json[field]
                
                # 해시태그 처리
                if 'hashtags' in parsed_json:
                    if isinstance(parsed_json['hashtags'], str):
                        # 문자열 형태의 해시태그 처리
                        hashtags_text = parsed_json['hashtags'].strip()
                        if '#' in hashtags_text:
                            result['hashtags'] = hashtags_text.split()
                        else:
                            result['hashtags'] = [f"#{tag.strip()}" for tag in hashtags_text.split()]
                    elif isinstance(parsed_json['hashtags'], list):
                        # 리스트 형태의 해시태그 처리
                        result['hashtags'] = parsed_json['hashtags']
                        
            except json.JSONDecodeError:
                # JSON 파싱 오류 발생 - 다른 방식으로 처리
                pass
        
        # 4. JSON 파싱이 실패한 경우, 정규표현식으로 직접 추출
        # 필드별 추출 함수 정의
        def extract_field(field_name, content):
            # 1. "field_name":"value" 형태 처리
            pattern = r'"' + field_name + r'"\s*:\s*"(.+?)(?:"|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip().replace('\\"', '"').replace('\\n', '\n')
            
            # 2. "field_name":\ 형태 처리 (빈 값 또는 이스케이프)
            pattern = r'"' + field_name + r'"\s*:\s*\\?\s*"?\s*(?:,|\}|$)'
            match = re.search(pattern, content)
            if match:
                return ""
                
            # 3. "field_name":value 형태 처리 (따옴표가 없는 값)
            pattern = r'"' + field_name + r'"\s*:\s*([^,\}\]\"]+)'
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
                
            return ""
        
        # 결과가 비어있는 경우에만 정규표현식으로 추출
        if 'blog_title' not in result:
            blog_title = extract_field('blog_title', content)
            result['blog_title'] = blog_title
                
        if 'blog_content' not in result:
            blog_content = extract_field('blog_content', content)
            result['blog_content'] = blog_content
                
        if 'headline' not in result:
            headline = extract_field('headline', content)
            result['headline'] = headline
                
        if 'caption' not in result:
            caption = extract_field('caption', content)
            result['caption'] = caption
        
        # 해시태그 추출(결과가 비어있는 경우에만)
        if 'hashtags' not in result:
            # 배열 형태의 해시태그 추출 시도
            hashtags_array_match = re.search(r'"hashtags"\s*:\s*\[\s*((?:"[^"]*"(?:\s*,\s*)?)*)\s*\]', content, re.DOTALL)
            if hashtags_array_match:
                hashtags_content = hashtags_array_match.group(1)
                # 각 해시태그 항목 추출
                hashtag_items = re.findall(r'"([^"]*)"', hashtags_content)
                result['hashtags'] = hashtag_items
            else:
                # 문자열 형태의 해시태그 추출
                hashtags_match = re.search(r'"hashtags"\s*:\s*"(.+?)"', content, re.DOTALL)
                if hashtags_match:
                    hashtags_text = hashtags_match.group(1).strip()
                    result['hashtags'] = hashtags_text.split()
                else:
                    result['hashtags'] = []
        
        # 5. 블로그 콘텐츠 보완 로직
        # 블로그 본문이 없는 경우 캡션으로 대체
        if 'blog_title' in result and 'blog_content' not in result and 'caption' in result:
            result['blog_content'] = result['caption']
            
        # 블로그 제목이 없는 경우 헤드라인으로 대체
        if 'blog_title' not in result and 'headline' in result:
            result['blog_title'] = result['headline']
        
        return result
        
    except Exception as e:
        st.error(f"⚠️ 응답 처리 중 오류 발생: {str(e)}")
        # 오류 발생 시 원래 데이터 반환
        return response_data
