import streamlit as st
import streamlit_shadcn_ui as ui
import re
import json
import pyperclip
from datetime import datetime

def show_input_form():
    """광고 생성을 위한 입력 폼 표시"""
    with st.form(key="ad_form"):
        st.markdown("## 📝 광고 정보 입력")
        
        # 웹: 2줄 2개씩, 모바일: 4줄 1개씩 (라벨과 드롭다운 가로 배치)
        col1, col2 = st.columns(2)
        
        with col1:
            platform_col1, platform_col2 = st.columns([1, 2])
            with platform_col1:
                st.write("플랫폼 선택:")
            with platform_col2:
                platform = st.selectbox(
                    "플랫폼 선택",
                    options=["인스타그램", "블로그"],
                    key="platform_select",
                    label_visibility="collapsed"
                )
        
        with col2:
            age_col1, age_col2 = st.columns([1, 2])
            with age_col1:
                st.write("타겟 연령대:")
            with age_col2:
                age_group = st.selectbox(
                    "타겟 연령대",
                    options=["10대", "20대", "30대", "40대", "50대", "60대", "70대", "80대+"],
                    key="age_group_select",
                    label_visibility="collapsed"
                )
        
        col3, col4 = st.columns(2)
        
        with col3:
            gender_col1, gender_col2 = st.columns([1, 2])
            with gender_col1:
                st.write("성별:")
            with gender_col2:
                gender = st.selectbox(
                    "성별",
                    options=["여성", "남성", "전체"],
                    key="gender_select",
                    label_visibility="collapsed"
                )
        
        with col4:
            concern_col1, concern_col2 = st.columns([1, 2])
            with concern_col1:
                st.write("피부고민:")
            with concern_col2:
                skin_concern = st.selectbox(
                    "피부고민 선택",
                    options=[
                        "모공 / 요철 / 각질",
                        "붉음증 / 예민 피부 / 얇은 피부", 
                        "색소 (기미, 잡티) / 미백",
                        "노화 / 주름 / 탄력",
                        "여드름 / 아토피 / 건선 / 흉터"
                    ],
                    key="skin_concern_select",
                    label_visibility="collapsed"
                )
        
        st.write("메시지를 자유롭게 작성해도, 광고법에 따라 작성됩니다.")
        customer_message = st.text_area(
            "원장님 메시지",
            placeholder="이 고객님을 관리하면서 기억에 남는 부분을 작성해주세요.",
            key="customer_message_textarea",
            label_visibility="collapsed"
        )
        
        # 추가 정보 입력 섹션
        st.markdown("### 📞 인스타 최적화에 필요한 정보")
        st.write("")
        
        # 3개 컬럼으로 배치
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            phone_col1, phone_col2 = st.columns([1, 2])
            with phone_col1:
                st.write("매장 / 폰 번호:")
            with phone_col2:
                phone_number = st.text_input(
                    "매장 / 폰 번호",
                    placeholder="010????????",
                    key="phone_number_input",
                    label_visibility="collapsed"
                )
        
        with info_col2:
            region_col1, region_col2 = st.columns([1, 2])
            with region_col1:
                st.write("지역명:")
            with region_col2:
                region = st.text_input(
                    "지역명",
                    placeholder="청주",
                    key="region_input",
                    label_visibility="collapsed"
                )
        
        with info_col3:
            shop_col1, shop_col2 = st.columns([1, 2])
            with shop_col1:
                st.write("샵명:")
            with shop_col2:
                shop_name = st.text_input(
                    "샵명",
                    placeholder="바이오폭스 강남점",
                    key="shop_name_input",
                    label_visibility="collapsed"
                )
        
        # 주의사항 표시 (광고 생성 전)
        st.markdown("""
        <div style="
            background-color: #fff3cd; 
            border: 1px solid #ffeaa7; 
            border-radius: 8px; 
            padding: 12px; 
            margin: 15px 0;
            border-left: 4px solid #f39c12;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">⚠️</span>
                <strong style="color: #856404;">주의사항</strong>
            </div>
            <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.4;">
                AI가 생성한 콘텐츠는 부적절하거나 부정확한 내용을 포함할 수 있습니다.<br>
                최종 사용 및 게시에 대한 책임은 사용자에게 있으며, 사용 전 반드시 내용을 검토하여 수정 후 사용하세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_submit = st.columns([1, 1, 1])
        with col_submit[1]:
            submit_button = st.form_submit_button(
                label="✨ 광고 생성하기",
                use_container_width=True
            )
        
        if submit_button:
            # 폼 데이터 수집
            form_data = {
                "platform": platform,
                "age": age_group,
                "gender": gender,
                "concern": skin_concern,
                "message": customer_message,
                "phone": phone_number,
                "region": region,
                "shop_name": shop_name
            }
            
            # 세션 상태에 저장
            st.session_state.form_data = form_data
            
            # 결과 생성 함수 호출
            return form_data
            
    return None

def show_results():
    """광고 생성 결과 표시"""
    if not st.session_state.get('result'):
        return
    
    result = st.session_state.result
    
    # 플랫폼 정보 가져오기 (기본값은 인스타그램)
    platform = st.session_state.get('form_data', {}).get('platform', '인스타그램')
    
    # CSS 스타일 적용 - 전체 페이지에 적용되는 스타일
    st.markdown("""
    <style>
        .ad-container {
            border: 1px solid #e1e4e8;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .ad-headline {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            line-height: 1.4;
        }
        .ad-caption, .blog-content {
            white-space: pre-wrap;
            line-height: 1.6;
            color: #444;
            max-height: 1000px;
            min-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            font-size: 1.05em;
            overflow-x: hidden;
        }
        .blog-title {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            line-height: 1.4;
            padding: 10px 15px;
            background-color: #f0f4f8;
            border-radius: 5px;
        }
        .hashtags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }
        .hashtag {
            background-color: #e1f5fe;
            color: #0277bd;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }
        .copy-btn {
            margin-top: 10px;
        }
        .version-selector {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f1f3f4;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 제목 표시
    st.markdown("## 🏁 생성된 광고", help="LLM이 생성한 광고 결과입니다")
    
    # 주의사항 표시
    st.markdown("""
    <div style="
        background-color: #fff3cd; 
        border: 1px solid #ffeaa7; 
        border-radius: 8px; 
        padding: 12px; 
        margin: 10px 0;
        border-left: 4px solid #f39c12;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="font-size: 16px; margin-right: 8px;">⚠️</span>
            <strong style="color: #856404;">주의사항</strong>
        </div>
        <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.4;">
            AI가 생성한 콘텐츠는 부적절하거나 부정확한 내용을 포함할 수 있습니다.<br>
            최종 사용 및 게시에 대한 책임은 사용자에게 있으며, 사용 전 반드시 내용을 검토하여 수정 후 사용하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 버전 관리 UI
    if 'version_history' in st.session_state and len(st.session_state.version_history) > 1:
        with st.container():
            st.markdown("<div class='version-selector'>", unsafe_allow_html=True)
            
            versions = [f"버전 {v['version']} ({v['timestamp']})" for v in st.session_state.version_history]
            current_version = f"버전 {st.session_state.version_history[-1]['version']} ({st.session_state.version_history[-1]['timestamp']})"
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("#### 버전 관리")
            
            with col2:
                selected_version = st.selectbox(
                    "버전 선택",
                    options=versions,
                    key="selected_version_select"
                )
            
            # 선택한 버전 문자열에서 버전 번호 추출
            version_idx = versions.index(selected_version) + 1 if selected_version in versions else len(versions)
            selected_version = version_idx
            
            # 선택한 버전이 현재 버전과 다른 경우 해당 버전 표시
            if selected_version != len(versions):
                from app import restore_version
                restore_version(selected_version)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 플랫폼 별 헤드라인 처리
    # 인스타그램에서만 후킹 문구 표시 (블로그는 제외)
    if platform == '인스타그램' and 'headline' in result and result['headline']:
        with st.container():
            st.markdown("""
            <div class="ad-container">
                <h3>📣 후킹 문구</h3>
                <div class="ad-headline">"{0}"</div>
            </div>
            """.format(result['headline']), unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col2:
                copy_headline = st.button("복사", key="copy_headline_btn")
                if copy_headline:
                    try:
                        pyperclip.copy(result['headline'])
                        st.success("헤드라인이 복사되었습니다!")
                    except Exception as e:
                        st.error(f"복사 중 오류 발생: {str(e)}")
    
    # 플랫폼에 따른 출력 처리
    if platform == '인스타그램':
        # 인스타그램 캡션 표시
        if 'caption' in result:
            with st.container():
                # 캡션 텍스트 처리
                # 1. 줄바꾸을 HTML <br>태그로 변환
                # 2. 해시태그 강조
                formatted_caption = result['caption'].replace('\n', '<br>')
                
                # 해시태그 강조 (#태그 스타일 적용)
                for tag in re.findall(r'#(\w+)', formatted_caption):
                    formatted_caption = formatted_caption.replace(
                        f'#{tag}', 
                        f'<span style="color: #1DA1F2; font-weight: 600;">#{tag}</span>'
                    )
                
                st.markdown("""
                <div class="ad-container">
                    <h3>📱 인스타그램 캡션</h3>
                    <div class="ad-caption">{0}</div>
                </div>
                """.format(formatted_caption), unsafe_allow_html=True)
                
                # 복사 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    copy_caption = st.button("복사", key="copy_caption_btn")
                    if copy_caption:
                        try:
                            pyperclip.copy(result['caption'])
                            st.success("캡션이 복사되었습니다!")
                        except Exception as e:
                            st.error(f"복사 중 오류 발생: {str(e)}")
        
        # 해시태그 표시
        if 'hashtags' in result and result['hashtags']:
            with st.container():
                # 해시태그 안전하게 처리
                hashtags_html = ""
                if isinstance(result['hashtags'], list):
                    # 각 해시태그를 전체 태그로 처리
                    hashtags_html = ''.join([f'<span class="hashtag">{tag if isinstance(tag, str) else ""}</span>' for tag in result['hashtags']])
                
                st.markdown("""
                <div class="ad-container">
                    <h3>🏷️ 해시태그</h3>
                    <div class="hashtags">{0}</div>
                </div>
                """.format(hashtags_html), unsafe_allow_html=True)
                
                # 복사 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    copy_hashtags = st.button("해시태그 복사", key="copy_hashtags_btn")
                    if copy_hashtags:
                        try:
                            hashtags_text = ' '.join(result['hashtags'])
                            pyperclip.copy(hashtags_text)
                            st.success("해시태그가 복사되었습니다!")
                        except Exception as e:
                            st.error(f"복사 중 오류 발생: {str(e)}")
    
    else:  # 블로그인 경우
        # 블로그 제목 표시
        if 'blog_title' in result:
            with st.container():
                # 블로그 제목을 안전하게 처리
                blog_title = ""
                if 'blog_title' in result and result['blog_title'] is not None:
                    # 이스케이프 문자 처리
                    title = str(result['blog_title'])
                    # JSON에서 이스케이프된 문자열 처리
                    if title.startswith('\\'): 
                        title = title[1:]
                    blog_title = title
                
                st.markdown("""
                <div class="ad-container">
                    <h3>📝 블로그 제목</h3>
                    <div class="blog-title">{0}</div>
                </div>
                """.format(blog_title), unsafe_allow_html=True)
                
                # 복사 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    copy_title = st.button("복사", key="copy_title_btn")
                    if copy_title:
                        try:
                            pyperclip.copy(result['blog_title'])
                            st.success("블로그 제목이 복사되었습니다!")
                        except Exception as e:
                            st.error(f"복사 중 오류가 발생했습니다: {str(e)}")
        
        # 블로그 본문 표시
        if 'blog_content' in result:
            with st.container():
                # 제목 표시
                st.markdown("### 📄 블로그 본문")
                
                # 원본 데이터 가져오기
                raw_content = result['blog_content']
                
                # 데이터가 JSON 문자열이거나 단일 백슬래시만 있는 경우
                if raw_content == '\\' or raw_content == '' or not raw_content or str(raw_content).strip() == '':
                    # 웹훅에서 원본 데이터 확인
                    st.warning("⚠️ 블로그 본문 데이터가 누락되었습니다.")
                    
                    # 캡션이 있는 경우 대체 표시
                    if 'caption' in result and result['caption']:
                        st.info("💡 대신 인스타그램 캡션을 표시합니다:")
                        st.text_area("", 
                                    value=result['caption'],
                                    height=400, 
                                    label_visibility="collapsed",
                                    key="blog_content_fallback")
                    else:
                        st.error("❌ 표시할 콘텐츠가 없습니다. 다시 생성해주세요.")
                else:
                    # 1. 일반 텍스트로 처리
                    try:
                        # JSON 문자열인 경우 처리 시도
                        import json
                        try:
                            # JSON 파싱 시도
                            if isinstance(raw_content, str) and ('{' in raw_content or '[' in raw_content):
                                json_data = json.loads(raw_content)
                                if isinstance(json_data, dict) and 'blog_content' in json_data:
                                    raw_content = json_data['blog_content']
                        except:
                            pass
                            
                        # 문자열 처리
                        content = str(raw_content)
                        # 줄바꿈 처리
                        content = content.replace('\\n', '\n')
                        # 따옴표 처리
                        content = content.replace('\\"', '"')
                        # 일반 백슬래시 처리
                        content = content.replace('\\\\', '\\')
                        
                        # 최종 표시 형식
                        st.text_area("", 
                                    value=content,
                                    height=400, 
                                    label_visibility="collapsed",
                                    key="blog_content_text")
                        
                    except Exception as e:
                        st.error(f"블로그 본문 표시 오류: {str(e)}")
                        # 원본 데이터 그대로 표시
                        st.text_area("", 
                                    value=str(raw_content),
                                    height=400, 
                                    label_visibility="collapsed",
                                    key="blog_content_raw")
                
                # 복사 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    copy_content = st.button("복사", key="copy_content_btn_text")
                    if copy_content:
                        try:
                            content_to_copy = content if 'content' in locals() else str(raw_content)
                            pyperclip.copy(content_to_copy)
                            st.success("블로그 본문이 복사되었습니다!")
                        except Exception as e:
                            st.error(f"복사 중 오류가 발생했습니다: {str(e)}")
        
        # 인스타그램 응답이 들어왔는데 블로그로 표시해야 하는 경우의 대체 처리
        elif 'caption' in result:
            with st.container():
                st.markdown("""
                <div class="ad-container">
                    <h3>📄 블로그 본문</h3>
                    <div class="blog-content">{0}</div>
                </div>
                """.format(result['caption'].replace('\n', '<br>')), unsafe_allow_html=True)
                
                # 복사 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    copy_content = st.button("복사", key="copy_content_btn")
                    if copy_content:
                        try:
                            pyperclip.copy(result['caption'])
                            st.success("블로그 본문이 복사되었습니다!")
                        except Exception as e:
                            st.error(f"복사 중 오류가 발생했습니다: {str(e)}")
        
    # 태그 표시 (블로그에서만 표시)
    if platform == '블로그' and 'hashtags' in result and result['hashtags']:
        with st.container():
            # CSS 스타일 추가
            st.markdown("""
            <style>
            .hashtag-container {
                margin-top: 15px;
                margin-bottom: 15px;
            }
            .hashtag {
                background-color: #f0f2f6;
                color: #0066cc;
                padding: 5px 10px;
                margin-right: 8px;
                margin-bottom: 8px;
                border-radius: 15px;
                display: inline-block;
                font-size: 0.9em;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 해시태그 안전하게 처리
            st.markdown("### 🏷️ 태그")
            
            # 태그 표시 영역
            tag_area = st.container()
            with tag_area:
                if isinstance(result['hashtags'], list):
                    # 태그 목록을 깨끗하게 표시
                    tags_html = '<div class="hashtag-container">'
                    
                    # 해시태그와 문자열 처리
                    processed_tags = []
                    for tag in result['hashtags']:
                        if isinstance(tag, str):
                            # 특수 문자 제거
                            tag = tag.strip()
                            if tag:
                                # 해시태그 '#' 처리
                                if not tag.startswith('#'):
                                    tag = f'#{tag}'
                                # 중복 해시태그 제거
                                if tag not in processed_tags:
                                    processed_tags.append(tag)
                    
                    # 해시태그 HTML 생성
                    for tag in processed_tags:
                        # 태그에서 HTML 특수문자 이스케이프 처리
                        tag_escaped = tag.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        tags_html += f'<span class="hashtag">{tag_escaped}</span>'
                        
                    tags_html += '</div>'
                    st.markdown(tags_html, unsafe_allow_html=True)
                    
                    # 업데이트된 태그 목록 저장 (복사용)
                    st.session_state['processed_hashtags'] = processed_tags
            
            # 복사 버튼
            col1, col2 = st.columns([3, 1])
            with col2:
                copy_tags = st.button("복사", key="copy_tags_btn")
                if copy_tags:
                    try:
                        # 처리된 해시태그 복사
                        if 'processed_hashtags' in st.session_state and st.session_state['processed_hashtags']:
                            # 처리된 태그 목록 사용
                            tags_text = ' '.join(st.session_state['processed_hashtags'])
                        else:
                            # 원본 태그 사용
                            processed_tags = []
                            if isinstance(result['hashtags'], list):
                                for tag in result['hashtags']:
                                    if isinstance(tag, str):
                                        tag = tag.strip()
                                        if tag and not tag.startswith('#'):
                                            tag = f'#{tag}'
                                        if tag and tag not in processed_tags:
                                            processed_tags.append(tag)
                                tags_text = ' '.join(processed_tags)
                            else:
                                tags_text = str(result['hashtags'])
                                
                        # 두 해시태그 사이에 공백 추가
                        pyperclip.copy(tags_text)
                        st.success("태그가 복사되었습니다!")
                    except Exception as e:
                        st.error(f"복사 중 오류가 발생했습니다: {str(e)}")

def show_chat_interface():
    """광고 수정을 위한 채팅 인터페이스"""
    if not st.session_state.get('chat_enabled'):
        return
    
    st.markdown("## 💬 광고 수정 요청")
    
    # 이전 메시지 표시
    for message in st.session_state.get('messages', []):
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])
    
    # 채팅 입력
    user_input = st.chat_input("수정 사항을 입력하세요...")
    
    if user_input:
        from app import handle_chat_input
        handle_chat_input(user_input)
        
        # 새로고침하여 수정된 내용 표시
        st.rerun()

def init_page():
    """페이지 기본 설정"""
    # 페이지 설정
    st.set_page_config(
        page_title="BIOFOX 광고 생성기",
        page_icon="✨",
        layout="centered"
    )
    
    # CSS 스타일
    st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
        }
        @media (max-width: 768px) {
            .stColumns > div {
                margin-bottom: 1rem;
            }
        }
        /* 드롭다운 메뉴 열렸을 때 옵션들의 폰트 크기만 조정 */
        .stSelectbox [role="listbox"] [role="option"] {
            font-size: 11px !important;
            white-space: nowrap !important;
            padding: 6px 10px !important;
            line-height: 1.2 !important;
        }
        
        /* 드롭다운 메뉴의 전체 컨테이너 */
        .stSelectbox [role="listbox"] {
            max-height: 300px !important;
            overflow-y: auto !important;
        }
    </style>
    """, unsafe_allow_html=True)
