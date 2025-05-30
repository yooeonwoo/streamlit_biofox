I'll search for the streamlit-shadcn-ui documentation to provide detailed UI implementation guidelines.

Let me search for more specific documentation about the components available in streamlit-shadcn-ui.

# 📋 BIOFOX 에스테틱 광고 생성기 - Streamlit 구현 PRD

## 1. 프로젝트 개요

### 1.1 목적
Streamlit과 streamlit-shadcn-ui를 활용하여 에스테틱 원장님들이 광고법을 준수하는 마케팅 문구를 쉽게 생성하고 수정할 수 있는 웹 애플리케이션 구현

### 1.2 핵심 기능
- 간단한 폼 입력으로 광고 문구 생성
- 채팅 인터페이스를 통한 실시간 수정
- 원클릭 복사 기능

## 2. 기술 사양

### 2.1 필수 패키지
```bash
pip install streamlit streamlit-shadcn-ui requests
```

### 2.2 환경 변수
```python
# .env 파일
N8N_WEBHOOK_URL=https://biofox.app.n8n.cloud/webhook/777ee576-1a99-4959-a4af-2ee6ce55454d
N8N_MODIFY_WEBHOOK_URL=https://biofox.app.n8n.cloud/webhook/[수정용-webhook-id]
```

## 3. UI 구현 상세

### 3.1 전체 레이아웃

streamlit-shadcn-ui는 shadcn 컴포넌트를 Streamlit에서 사용할 수 있게 해주는 라이브러리로, ui.card, ui.button, ui.element 등의 컴포넌트를 제공합니다.

```python
import streamlit as st
import streamlit_shadcn_ui as ui

# 페이지 설정
st.set_page_config(
    page_title="BIOFOX 광고 생성기",
    page_icon="✨",
    layout="centered"
)

# 헤더
st.title("✨ BIOFOX 에스테틱 광고 생성기")
ui.badges(
    badge_list=[("BIOFOX", "default"), ("×", "secondary"), ("MICROJET", "destructive")],
    class_name="flex gap-2",
    key="header_badges"
)
```

### 3.2 입력 폼 구현

#### 3.2.1 컨테이너 구조
ui.card를 사용하여 카드 형태의 컨테이너를 만들고, ui.tabs로 탭 네비게이션을 구현할 수 있습니다.

```python
# 메인 입력 폼
with ui.card(key="input_form_card"):
    st.subheader("📝 광고 정보 입력")
    
    # 2열 레이아웃
    col1, col2 = st.columns(2)
    
    with col1:
        # 플랫폼 선택 (shadcn select 스타일)
        platform = st.selectbox(
            "플랫폼 선택",
            ["인스타그램", "블로그"],
            key="platform_select"
        )
        
        # 스타일 선택
        style = st.selectbox(
            "후킹 스타일",
            ["요약/일관성", "강한 후킹", "감정 자극"],
            key="style_select"
        )
    
    with col2:
        # 연령대 선택
        age = st.selectbox(
            "타겟 연령대",
            ["20대", "30대", "40대", "50대+"],
            key="age_select"
        )
        
        # 고객 고민 입력
        concern = st.text_input(
            "타겟 고객 고민",
            placeholder="예: 기미, 나비존, 모공 등",
            max_chars=100,
            key="concern_input"
        )
    
    # 원장님 메시지 (전체 너비)
    message = st.text_area(
        "원장님 메시지",
        placeholder="예: 15년 경력, BIOFOX × MICROJET 전문",
        max_chars=200,
        height=100,
        key="message_textarea"
    )
```

#### 3.2.2 생성 버튼
ui.button으로 shadcn 스타일의 버튼을 만들 수 있고, variant 옵션으로 스타일을 지정할 수 있습니다.

```python
# 생성 버튼 (shadcn 스타일)
generate_clicked = ui.button(
    text="✨ 광고 생성하기",
    key="generate_btn",
    class_name="w-full"
)
```

### 3.3 결과 표시 구현

#### 3.3.1 구조화된 결과
```python
if st.session_state.get('result'):
    result = st.session_state.result
    
    # 성공 알림
    st.success("✨ 광고 생성 완료!")
    
    # 결과 카드
    with ui.card(key="result_card"):
        # 광고문구 섹션
        st.subheader("📝 광고문구")
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # 강조 표시를 위한 커스텀 스타일
            st.markdown(
                f"""
                <div style="
                    background-color: #f0f9ff;
                    padding: 20px;
                    border-radius: 8px;
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                ">
                {result['headline']}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            if ui.button("📋", key="copy_headline", variant="outline"):
                st.toast("광고문구가 복사되었습니다!")
        
        # 캡션 섹션
        st.subheader("📱 인스타그램 캡션")
        caption_container = st.container()
        with caption_container:
            st.text_area(
                "",
                value=result['caption'],
                height=200,
                disabled=True,
                key="caption_display"
            )
            
            if ui.button("📋 복사", key="copy_caption", variant="outline"):
                st.toast("캡션이 복사되었습니다!")
        
        # 해시태그 섹션
        st.subheader("🏷️ 해시태그")
        hashtags_text = " ".join(result['hashtags'])
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.code(hashtags_text)
        with col2:
            if ui.button("📋", key="copy_hashtags", variant="outline"):
                st.toast("해시태그가 복사되었습니다!")
```

#### 3.3.2 액션 버튼
```python
# 전체 액션 버튼
col1, col2 = st.columns(2)

with col1:
    if ui.button(
        "📥 전체 내용 복사",
        key="copy_all",
        variant="default",
        class_name="w-full"
    ):
        full_content = f"""광고문구: {result['headline']}

{result['caption']}

{hashtags_text}"""
        st.toast("전체 내용이 복사되었습니다!")

with col2:
    if ui.button(
        "🔄 다시 생성하기",
        key="regenerate",
        variant="outline",
        class_name="w-full"
    ):
        st.session_state.clear()
        st.rerun()
```

### 3.4 채팅 인터페이스 구현

#### 3.4.1 채팅 UI
```python
# 채팅 섹션
if st.session_state.get('chat_enabled'):
    st.divider()
    
    with ui.card(key="chat_card"):
        st.subheader("💬 추가 요청사항이 있으신가요?")
        
        # 안내 메시지
        with st.chat_message("assistant"):
            st.write("생성된 광고를 수정하거나 다른 스타일로 변경해드릴 수 있어요.")
            st.write("예시:")
            st.write("• 좀 더 부드럽게 바꿔주세요")
            st.write("• 20대 느낌으로 수정해주세요")
            st.write("• 이모지를 더 추가해주세요")
        
        # 빠른 수정 버튼
        st.write("**빠른 수정:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            soft_btn = ui.button("😊 더 부드럽게", key="soft_btn", variant="secondary", size="sm")
        with col2:
            strong_btn = ui.button("💪 더 강하게", key="strong_btn", variant="secondary", size="sm")
        with col3:
            short_btn = ui.button("🎯 더 짧게", key="short_btn", variant="secondary", size="sm")
        
        # 채팅 히스토리
        for message in st.session_state.get('messages', []):
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # 사용자 입력
        if prompt := st.chat_input("수정 요청을 입력하세요"):
            handle_chat_input(prompt)
```

#### 3.4.2 버전 관리
```python
# 이전 버전 관리
if len(st.session_state.get('version_history', [])) > 1:
    with st.expander("📚 버전 히스토리"):
        for idx, version in enumerate(st.session_state.version_history):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"버전 {idx + 1}: {version['timestamp']}")
            with col2:
                if ui.button("보기", key=f"view_{idx}", size="sm"):
                    display_version(version)
            with col3:
                if ui.button("복원", key=f"restore_{idx}", size="sm"):
                    restore_version(version)
```

## 4. 핵심 기능 구현

### 4.1 n8n 통신
```python
import requests
import os
from datetime import datetime

def call_n8n_webhook(data, webhook_type="generate"):
    """n8n webhook 호출"""
    webhook_url = os.getenv(
        "N8N_WEBHOOK_URL" if webhook_type == "generate" else "N8N_MODIFY_WEBHOOK_URL"
    )
    
    try:
        response = requests.post(
            webhook_url,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ 요청 시간이 초과되었습니다. 다시 시도해주세요.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        return None

def generate_content(form_data):
    """광고 컨텐츠 생성"""
    with st.spinner("✨ 광고를 생성하고 있습니다..."):
        result = call_n8n_webhook({
            "type": "generate",
            "data": form_data
        })
        
        if result and result.get('status') == 'success':
            # 결과 저장
            st.session_state.result = result['data']
            st.session_state.chat_enabled = True
            st.session_state.messages = []
            st.session_state.version_history = [{
                'version': 1,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'data': result['data']
            }]
            return True
    return False
```

### 4.2 채팅 처리
```python
def handle_chat_input(user_input):
    """채팅 입력 처리"""
    # 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 수정 요청
    with st.spinner("✏️ 수정 중..."):
        modify_data = {
            "type": "modify",
            "data": {
                "original_result": st.session_state.result,
                "user_request": user_input,
                "context": st.session_state.get('form_data', {})
            }
        }
        
        result = call_n8n_webhook(modify_data, webhook_type="modify")
        
        if result and result.get('status') == 'success':
            # 수정된 결과 업데이트
            modified_data = result['data']
            
            # 결과 업데이트
            if 'modified_headline' in modified_data:
                st.session_state.result['headline'] = modified_data['modified_headline']
            if 'modified_caption' in modified_data:
                st.session_state.result['caption'] = modified_data['modified_caption']
            
            # 버전 히스토리 추가
            st.session_state.version_history.append({
                'version': len(st.session_state.version_history) + 1,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'data': st.session_state.result.copy()
            })
            
            # AI 응답 추가
            response_message = modified_data.get('message', '수정이 완료되었습니다.')
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_message
            })
            
            st.rerun()
```

### 4.3 세션 상태 초기화
```python
def init_session_state():
    """세션 상태 초기화"""
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'chat_enabled' not in st.session_state:
        st.session_state.chat_enabled = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'version_history' not in st.session_state:
        st.session_state.version_history = []
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
```

## 5. 메인 앱 구조

```python
# app.py
import streamlit as st
import streamlit_shadcn_ui as ui
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

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
</style>
""", unsafe_allow_html=True)

def main():
    # 세션 상태 초기화
    init_session_state()
    
    # 헤더
    st.title("✨ BIOFOX 에스테틱 광고 생성기")
    ui.badges(
        badge_list=[("BIOFOX", "default"), ("×", "secondary"), ("MICROJET", "destructive")],
        class_name="flex gap-2",
        key="header_badges"
    )
    
    # 결과가 없으면 입력 폼 표시
    if not st.session_state.result:
        show_input_form()
    else:
        show_results()
        show_chat_interface()

if __name__ == "__main__":
    main()
```

## 6. 배포 설정

### 6.1 requirements.txt
```
streamlit==1.28.0
streamlit-shadcn-ui==0.1.18
requests==2.31.0
python-dotenv==1.0.0
```

### 6.2 .streamlit/config.toml
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 5
```

## 7. 개발 가이드

### 7.1 로컬 개발
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
echo "N8N_WEBHOOK_URL=your_webhook_url" > .env

# 실행
streamlit run app.py
```

### 7.2 주요 shadcn-ui 컴포넌트 활용
streamlit-shadcn-ui는 ui.card, ui.button, ui.element, ui.badges, ui.tabs 등의 컴포넌트를 제공하며, variant와 class_name 속성으로 스타일을 커스터마이징할 수 있습니다.

- **ui.card()**: 카드 컨테이너
- **ui.button()**: 버튼 (variant: default, outline, secondary, destructive)
- **ui.badges()**: 배지 리스트
- **ui.element()**: 범용 HTML 요소
- **ui.tabs()**: 탭 네비게이션

---

**프로젝트 완료 체크리스트:**
- [ ] 환경 변수 설정 (.env)
- [ ] n8n webhook URL 설정
- [ ] Streamlit 앱 구현
- [ ] 모바일 반응형 테스트
- [ ] 에러 처리 구현
- [ ] Streamlit Cloud 배포