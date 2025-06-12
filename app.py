import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import openai # Import the openai library

# Set Streamlit page config
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")


# Custom CSS for styling
# Load custom CSS from style.css file
try:
    with open('style.css', encoding='utf-8') as f: # <-- 여기에 encoding='utf-8' 추가
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.error("Error: style.css not found. Please make sure style.css is in the same directory.")
    st.stop()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = ''
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'address' not in st.session_state:
    st.session_state.address = ''
if 'checkboxes' not in st.session_state:
    st.session_state.checkboxes = {
        'check1_elderly': False, 'check2_elderly': False, 'check3_elderly': False,
        'check1_foreigner': False, 'check2_foreigner': False, 'check3_foreigner': False,
    }
if 'ai_report_content' not in st.session_state:
    st.session_state.ai_report_content = None

# Set OpenAI API key
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("OpenAI API key not found in secrets.toml. Please add it.")
    st.stop() # Stop the app if the key is not found

def set_page(page_index):
    st.session_state.current_page = page_index
    st.rerun()

def check_form_validity():
    name_filled = bool(st.session_state.name.strip())
    address_filled = bool(st.session_state.address.strip())

    correct_checkboxes_selected = True
    if st.session_state.selected_role == 'elderly':
        if not st.session_state.checkboxes['check1_elderly']:
            correct_checkboxes_selected = False
        if st.session_state.checkboxes['check2_elderly']:
            correct_checkboxes_selected = False
        if not st.session_state.checkboxes['check3_elderly']:
            correct_checkboxes_selected = False
    elif st.session_state.selected_role == 'foreigner':
        if not st.session_state.checkboxes['check1_foreigner']:
            correct_checkboxes_selected = False
        if st.session_state.checkboxes['check2_foreigner']:
            correct_checkboxes_selected = False
        if not st.session_state.checkboxes['check3_foreigner']:
            correct_checkboxes_selected = False

    return name_filled and address_filled and correct_checkboxes_selected

# --- AI Report Generation Function (MODIFIED) ---
def get_ai_report(role, form_data, elapsed_time_seconds):
    # Construct the prompt for GPT
    prompt = f"""
        당신은 사용자가 겪은 어려움에 깊이 공감하고, 디지털 포용의 중요성을 알기 쉽게 설명해주는 '디지털 포용 경험 컨설턴트'입니다.
        사용자는 당신이 만든 '디지털 격차 시뮬레이션'에 참여했으며, 방금 과제를 마쳤습니다. 이제 그 경험을 바탕으로 개인화된 분석 리포트를 작성해주세요.

        [시뮬레이션 정보]
        - 부여된 역할: '{role}'
        - 폼 작성 소요 시간: {elapsed_time_seconds:.1f}초
        - 신청자 이름: '{form_data['name']}'

        [리포트 작성 지침]
        1.  **친절하고 공감적인 어투**를 사용하며, '{form_data['name']}님'처럼 사용자의 이름을 직접 불러주세요.
        2.  아래의 **4가지 섹션 구조**를 반드시 지켜서, 마크다운 형식으로 리포트를 작성해주세요.
        3.  핵심 키워드는 **볼드체**로 강조하고, 리스트는 글머리 기호(bullet point)를 사용해 가독성을 높여주세요.
        4.  각 섹션의 내용은 단순히 정보를 나열하는 것을 넘어, 사용자의 경험과 감정을 연결하여 의미를 부여해야 합니다.
        5.  전체 내용은 최소 300자 이상으로 풍부하게 작성해주세요.

        ---

        [리포트 양식]

        ## 📌 {form_data['name']}님이 마주한 '디지털 장벽' 분석

        '{role}' 역할로 폼을 작성하는 데 **{elapsed_time_seconds:.1f}초**가 걸렸습니다. 이 시간은 단순히 숫자를 넘어, {form_data['name']}님이 겪었을 **심리적, 인지적 부담**을 보여주는 지표입니다. 아마 익숙하지 않은 화면 구성이나 작은 글씨 때문에 망설이거나, 정보를 여러 번 확인하는 과정이 필요했을 수 있습니다. 이처럼 **사소하게 느껴지는 불편함**이 바로 디지털 세상에서 누군가는 매일 마주하는 '보이지 않는 장벽'입니다.

        ## 🔍 '{role}' 역할군이 겪는 현실적인 어려움

        {form_data['name']}님이 경험하신 어려움은 비단 개인의 문제만은 아닙니다. '{role}' 역할군이 디지털 환경에서 흔히 겪는 문제들은 다음과 같습니다.
        * **(어려움 1)**: [첫 번째 어려움을 구체적으로 서술]
        * **(어려움 2)**: [두 번째 어려움을 구체적으로 서술]
        * **(어려움 3)**: [세 번째 어려움을 구체적으로 서술]
        (예: 작은 글씨와 복잡한 UI로 인한 **시각적 피로감**, 전문 용어 사용으로 인한 **정보 이해의 어려움**, 복잡한 인증 절차에 대한 **심리적 불안감** 등)

        ## 💡 모두를 위한 디지털 세상을 만드는 구체적인 방법

        이러한 디지털 장벽을 허물기 위해 우리는 무엇을 할 수 있을까요? 몇 가지 구체적인 개선 방안을 제안합니다.
        * **디자인 측면**: [사용자 인터페이스(UI)와 관련된 개선 방안을 구체적으로 제안. 예: '글자 크기 조절 기능 추가', '직관적인 아이콘 사용']
        * **콘텐츠 측면**: [정보 제공 방식과 관련된 개선 방안을 제안. 예: '쉬운 용어 사용 및 설명 추가', '음성 안내(TTS) 기능 제공']
        * **사회적 측면**: [교육이나 정책과 관련된 개선 방안을 제안. 예: '찾아가는 디지털 교육 확대', '공공 키오스크에 접근성 가이드라인 의무화']

        ## ✨ 오늘의 경험이 우리에게 남긴 것

        오늘 {form_data['name']}님이 잠시나마 겪었던 불편함은, 우리 사회가 **'디지털 포용'**으로 나아가기 위해 풀어야 할 중요한 숙제입니다. 이 경험을 통해 나와 다른 입장의 사람들을 한 번 더 생각해볼 수 있는 계기가 되셨기를 바랍니다. 기술의 발전이 **소외가 아닌 연결**을 만드는 데 기여할 수 있도록, {form_data['name']}님의 작은 관심이 큰 변화의 시작이 될 수 있습니다.
        """

    try:
        with st.spinner("AI 분석 리포트를 생성 중입니다... 잠시만 기다려 주세요."):
            response = openai.chat.completions.create(
                model="gpt-4o", # You can choose other models like "gpt-3.5-turbo" if needed
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant specializing in digital inclusivity and user experience analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800, # Adjust as needed
                temperature=0.7, # Adjust creativity (0.0-1.0)
            )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI 리포트 생성 중 오류가 발생했습니다: {e}")
        return "AI 리포트를 불러올 수 없습니다. 오류가 발생했습니다."


# --- Chart Generation Function ---
import pandas as pd
import plotly.express as px

def create_digital_divide_charts():
    """
    고령층과 외국인의 소통 목적 인터넷 사용 현황에 대한
    두 개의 파이차트를 생성합니다.
    """

    # 1. 고령층 데이터 및 파이차트 생성
    elderly_data = pd.DataFrame({
        '사용 빈도': ['사용 안 함', '가끔 사용', '자주 사용', '항상 사용'],
        '응답자 수': [1475, 231, 193, 39]
    })

    fig1 = px.pie(
        elderly_data,
        values='응답자 수',
        names='사용 빈도',
        title='고령층의 소통 목적 인터넷 사용 현황',
        color_discrete_sequence=px.colors.sequential.Blues_r, # 파란색 계열
        hole=0.3 # 도넛 모양으로 만들기
    )

    # fig1 차트 디자인 업데이트
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label', # 차트 안에 퍼센트와 라벨 표시
        pull=[0.05, 0, 0, 0] # 가장 큰 조각을 약간 떼어내어 강조
    )
    fig1.update_layout(
        height=400,
        showlegend=False, # 범례는 숨김 (차트에 라벨이 표시되므로)
        title_font_size=16,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    # 2. 외국인 데이터 및 파이차트 생성
    foreigner_data = pd.DataFrame({
        '사용 빈도': ['사용 안 함', '가끔 사용', '자주 사용', '항상 사용'],
        '응답자 수': [435, 140, 58, 26]
    })

    fig2 = px.pie(
        foreigner_data,
        values='응답자 수',
        names='사용 빈도',
        title='외국인의 소통 목적 인터넷 사용 현황',
        color_discrete_sequence=px.colors.sequential.Reds_r,
        hole=0.3 # 도넛 모양으로 만들기
    )

    # fig2 차트 디자인 업데이트
    fig2.update_traces(
        textposition='inside',
        textinfo='percent+label',
        pull=[0.05, 0, 0, 0]
    )
    fig2.update_layout(
        height=400,
        showlegend=False,
        title_font_size=16,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig1, fig2

# --- Start conditional page rendering ---


# Page 1: Start Page
if st.session_state.current_page == 0:
    # 이제 content-box div 하나로 모든 것을 감쌉니다.
    # 상위 section이 중앙 정렬을 모두 처리해줍니다.
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    st.markdown('<h1>당신은 누구십니까?</h1>', unsafe_allow_html=True)
    st.markdown('<p>당신은 해당 역할로 지원금 신청서를 작성합니다.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="button-group">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button('75세 김OO씨', key='elderly_role_button'):
            st.session_state.selected_role = 'elderly'
            st.session_state.start_time = time.time()
            st.session_state.ai_report_content = None
            set_page(1)
    with col2:
        if st.button('외국인 회사원 ㅁㅁㅁ씨', key='foreigner_role_button'):
            st.session_state.selected_role = 'foreigner'
            st.session_state.start_time = time.time()
            st.session_state.ai_report_content = None
            set_page(1)
    st.markdown('</div>', unsafe_allow_html=True) # button-group 닫기
    
    st.markdown('</div>', unsafe_allow_html=True) # content-box 닫기


# Page 2: Application Form
elif st.session_state.current_page == 1:
    st.markdown('<div class="page-container page2">', unsafe_allow_html=True)
    # Add text to the top of Page 2
    # st.markdown('<p class="page2-top-intro">이 지원금은 디지털 격차 해소를 위해 제공됩니다. 다음 정보를 정확히 입력해 주세요.</p>', unsafe_allow_html=True)
    st.markdown('<h2>지원금 신청서</h2>', unsafe_allow_html=True)
    st.markdown('<p>다음 설문 신청 폼을 작성하여 지원금을 신청해주세요.</p>', unsafe_allow_html=True)

    st.markdown('<div class="page2-content">', unsafe_allow_html=True)

    if st.session_state.selected_role == 'elderly':
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<label for="name_elderly_input_text" class="elderly-label-normal">신청자 성명:</label>', unsafe_allow_html=True)
        st.session_state.name = st.text_input(
            label="Hidden Name Label",
            value=st.session_state.name,
            key="name_elderly_input",
            label_visibility="hidden" # This part is important!
        )
        st.markdown('<span class="elderly-small-text">(본인임을 증명할 수 있는 정식 한글 성함을 정자체로 기재해 주십시오. 임의 기재 시 신청이 반려될 수 있으며, 이는 전적으로 신청인의 책임으로 귀결됩니다.)</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<label for="address_elderly_input_text" class="elderly-label-normal">주소지</label>', unsafe_allow_html=True)
        st.session_state.address = st.text_input(
            label="Hidden Address Label",
            value=st.session_state.address,
            key="address_elderly_input",
            label_visibility="hidden" # This part is important!
        )
        st.markdown('<span class="elderly-small-text">(본 신청서에 기재된 주소지가 실제 주거 상태와 불일치함이 추후 발견될 시, 해당 신청은 별도 통보 없이 자격 상실 처리되며, 지급된 지원금은 관련 법규에 의거하여 환수될 수 있음을 고지합니다.)</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        with st.container():
            col_chk1, col_txt1 = st.columns([0.05, 0.95])
            with col_chk1:
                st.session_state.checkboxes['check1_elderly'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check1_elderly'],
                    key='check1_elderly_c'
                )
            with col_txt1:
                st.markdown('<label for="check1_elderly_c" class="elderly-tiny-checkbox-label">본인은 본 신청서에 기재한 모든 정보가 본인의 인식과 신념에 기반하여 진실되고 정확하다는 점을 이로써 확인하며, 만일 허위 사실의 기재 또는 사실의 왜곡·은폐 등이 발견될 경우, 본 신청은 즉시 자격이 박탈될 수 있으며, 나아가 대한민국 관련 법령 및 규정에 의거하여 민형사상 책임이 부과될 수 있음을 충분히 인지하고 이에 동의합니다. (필수 확인 사항입니다. 반드시 숙지하시고 체크하시오.)</label>', unsafe_allow_html=True)

        with st.container():
            col_chk2, col_txt2 = st.columns([0.05, 0.95])
            with col_chk2:
                st.session_state.checkboxes['check2_elderly'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check2_elderly'],
                    key='check2_elderly_c'
                )
            with col_txt2:
                st.markdown('<label for="check2_elderly_c" class="elderly-tiny-checkbox-label">본인은 본 신청서 및 이에 부속된 일체의 제출 서류가 제출과 동시에 주관 기관의 소유로 귀속되며, 어떠한 사유로도 반환되지 아니함을 인지하고 이에 동의하며, 아울러 본 신청의 제출 행위 자체가 해당 프로그램의 공식 운영 지침 및 향후 관계 당국에 의해 고지될 수 있는 모든 수정사항 및 보완 지시에 대하여 구속력을 갖는 준수 의무를 수반하는 법적 효력을 지닌다는 사실을 명확히 인식하고 이에 전적으로 동의합니다. (선택하지 마시오. 선택 시 심사에서 제외될 수 있습니다.)</label>', unsafe_allow_html=True)

        with st.container():
            col_chk3, col_txt3 = st.columns([0.05, 0.95])
            with col_chk3:
                st.session_state.checkboxes['check3_elderly'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check3_elderly'],
                    key='check3_elderly_c'
                )
            with col_txt3:
                st.markdown('<label for="check3_elderly_c" class="elderly-tiny-checkbox-label">본인은 본 항목에 체크함으로써, 본 디지털 포용 지원 프로그램에 부속된 모든 이용 약관, 세부 조건 및 개인정보 처리 방침을 공식 정부 포털을 통해 열람 가능한 통합 운영 지침에 따라 충분히 숙지하고 이에 명시적으로 동의함을 확인하며, 프로그램 전 기간에 걸쳐 명시된 모든 자격 요건을 지속적으로 충족할 것을 성실히 이행할 법적 및 행정적 책임이 본인에게 있음을 인지하고 이에 전적으로 동의합니다. (필수 확인 사항입니다. 반드시 숙지하시고 체크하시오.)</label>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.selected_role == 'foreigner':
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<label for="name_foreigner_input_text" class="foreigner-label-normal">Full Name / 성명 (여권 또는 공적 신분증명서상 기재된 사항에 준하여 입력되어야 하며, 제출된 정보와 공식 문서 간의 어떠한 불일치도 신청의 즉각적인 반려 사유가 될 수 있으며, 이에 따라 전 과정을 포함한 재신청 절차가 요구될 수 있습니다.):</label>', unsafe_allow_html=True)
        st.session_state.name = st.text_input(
            label="Hidden Foreigner Name Label",
            value=st.session_state.name,
            key="name_foreigner_input",
            label_visibility="hidden" # This part is important!
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<label for="address_foreigner_input_text" class="foreigner-label-normal">Residential Address / 거주지 주소 (귀하의 출신 국가에서 통용되는 표준 주소 표기 방식에 준하여, 우편번호를 포함한 현재 실거주지 주소 전체를 정확히 기재해 주시기 바랍니다. 아울러, 향후 주소지 변경이 발생할 경우에는 관계 당국에 지체 없이 이를 통지하여야 하며, 이를 소홀히 할 경우 각종 권익 또는 공식 통지의 수령과 관련하여 예기치 못한 불이익이나 행정적 차질이 발생할 수 있음을 유의하시기 바랍니다.):</label>', unsafe_allow_html=True)
        st.session_state.address = st.text_input(
            label="Hidden Foreigner Address Label",
            value=st.session_state.address,
            key="address_foreigner_input",
            label_visibility="hidden" # This part is important!
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        with st.container():
            col_chk1, col_txt1 = st.columns([0.05, 0.95])
            with col_chk1:
                st.session_state.checkboxes['check1_foreigner'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check1_foreigner'],
                    key='check1_foreigner_c'
                )
            with col_txt1:
                st.markdown('<label for="check1_foreigner_c" class="foreigner-tiny-checkbox-label">본인은 본 신청서에 기재한 모든 정보가 본인의 인식과 신념에 기반하여 진실되고 정확하다는 점을 이로써 확인하며, 만일 허위 사실의 기재 또는 사실의 왜곡·은폐 등이 발견될 경우, 본 신청은 즉시 자격이 박탈될 수 있으며, 나아가 대한민국 관련 법령 및 규정에 의거하여 민형사상 책임이 부과될 수 있음을 충분히 인지하고 이에 동의합니다. (필수 확인 사항입니다. 반드시 숙지하시고 체크하시오.)</label>', unsafe_allow_html=True)

        with st.container():
            col_chk2, col_txt2 = st.columns([0.05, 0.95])
            with col_chk2:
                st.session_state.checkboxes['check2_foreigner'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check2_foreigner'],
                    key='check2_foreigner_c'
                )
            with col_txt2:
                st.markdown('<label for="check2_foreigner_c" class="foreigner-tiny-checkbox-label">본인은 본 신청서 및 이에 부속된 일체의 제출 서류가 제출과 동시에 주관 기관의 소유로 귀속되며, 어떠한 사유로도 반환되지 아니함을 인지하고 이에 동의하며, 아울러 본 신청의 제출 행위 자체가 해당 프로그램의 공식 운영 지침 및 향후 관계 당국에 의해 고지될 수 있는 모든 수정사항 및 보완 지시에 대하여 구속력을 갖는 준수 의무를 수반하는 법적 효력을 지닌다는 사실을 명확히 인식하고 이에 전적으로 동의합니다. (선택하지 마시오. 선택 시 심사에서 제외될 수 있습니다.)</label>', unsafe_allow_html=True)

        with st.container():
            col_chk3, col_txt3 = st.columns([0.05, 0.95])
            with col_chk3:
                st.session_state.checkboxes['check3_foreigner'] = st.checkbox(
                    label="",
                    value=st.session_state.checkboxes['check3_foreigner'],
                    key='check3_foreigner_c'
                )
            with col_txt3:
                st.markdown('<label for="check3_foreigner_c" class="foreigner-tiny-checkbox-label">본인은 본 항목에 체크함으로써, 본 디지털 포용 지원 프로그램에 부속된 모든 이용 약관, 세부 조건 및 개인정보 처리 방침을 공식 정부 포털을 통해 열람 가능한 통합 운영 지침에 따라 충분히 숙지하고 이에 명시적으로 동의함을 확인하며, 프로그램 전 기간에 걸쳐 명시된 모든 자격 요건을 지속적으로 충족할 것을 성실히 이행할 법적 및 행정적 책임이 본인에게 있음을 인지하고 이에 전적으로 동의합니다. (필수 확인 사항입니다. 반드시 숙지하시고 체크하시오.)</label>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# app.py

# ... (기존 코드 유지) ...

    form_is_valid = check_form_validity()

    if not form_is_valid:
        if not (st.session_state.name.strip() and st.session_state.address.strip()):
            st.error("성명과 주소지를 모두 입력해야 합니다.")
        elif (st.session_state.selected_role == 'elderly' and (not st.session_state.checkboxes['check1_elderly'] or not st.session_state.checkboxes['check3_elderly'])) or \
             (st.session_state.selected_role == 'foreigner' and (not st.session_state.checkboxes['check1_foreigner'] or not st.session_state.checkboxes['check3_foreigner'])):
            st.error("필수 동의 항목에 체크해야 합니다.")
        elif (st.session_state.selected_role == 'elderly' and st.session_state.checkboxes['check2_elderly']) or \
             (st.session_state.selected_role == 'foreigner' and st.session_state.checkboxes['check2_foreigner']):
            st.error("두 번째 체크박스는 선택하지 마십시오. (선택 시 심사에서 제외될 수 있습니다.)")

    if st.button('신청', key='submit_form_button', disabled=not form_is_valid):
        st.session_state.end_time = time.time()
        # AI 리포트 생성 로직을 Page 3으로 이동시키기 위해,
        # 필요한 시간만 세션 상태에 저장하고 바로 페이지 전환
        st.session_state.elapsed_time_for_report = st.session_state.end_time - st.session_state.start_time
        st.session_state.ai_report_content = None # 리포트 내용을 초기화하여 로딩 스피너가 보이게 함
        set_page(2) # 바로 3페이지로 이동

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Page 3: AI Analysis Report
elif st.session_state.current_page == 2:
    st.markdown('<div class="page-container page3">', unsafe_allow_html=True)

    elapsed_time_seconds = 0
    if 'start_time' in st.session_state and 'end_time' in st.session_state:
        elapsed_time_seconds = st.session_state.end_time - st.session_state.start_time

    minutes = int(elapsed_time_seconds // 60)
    seconds = int(elapsed_time_seconds % 60)

    time_display = f"{minutes:02}:{seconds:02}"
    st.markdown(f'<div class="timer-display" id="elapsedTime">{time_display}</div>', unsafe_allow_html=True)

    st.markdown('<h2>AI 분석 리포트</h2>', unsafe_allow_html=True)

    # --- AI 리포트 생성 로직을 Page 3으로 이동 ---
    with st.container():
        # ai_report_content가 아직 없으면 생성 시작
        if st.session_state.ai_report_content is None:
            # st.spinner는 with 블록 안에서만 작동하므로, 여기에 넣어줍니다.
            # get_ai_report 함수 내부의 st.spinner는 제거하거나,
            # 여기서는 호출 전에 스피너를 보여줄 것이므로, get_ai_report 내 스피너는 불필요할 수 있습니다.
            # get_ai_report 함수는 그대로 두고 st.spinner를 감싸는 방식도 가능합니다.
            # 여기서는 get_ai_report 함수 내부에 이미 st.spinner가 있다고 가정합니다.
            
            # get_ai_report 함수 내부에 st.spinner가 있다면, 아래 주석을 풀고 사용
            st.session_state.ai_report_content = get_ai_report(
                st.session_state.selected_role,
                {'name': st.session_state.name, 'address': st.session_state.address},
                st.session_state.elapsed_time_for_report # Page 2에서 저장한 시간 사용
            )
        
        # 리포트 내용을 표시
        report_content = st.session_state.ai_report_content if st.session_state.ai_report_content else '<p>AI 리포트 생성 중...</p>'

        st.markdown(f"""
        <div class="ai-report-placeholder-wrapper">
            {report_content}
        </div>
        """, unsafe_allow_html=True)
    # --- End of AI 리포트 생성 로직 ---

    if st.button('마지막 결과 보기', key='final_result_button'):
        set_page(3)

    st.markdown('</div>', unsafe_allow_html=True)

# ... (기존 코드 유지) ...


# Page 4: Digital Divide Status
elif st.session_state.current_page == 3:
    st.markdown('<div class="page-container page4">', unsafe_allow_html=True)

    # 1. Apply light blue box to text and descriptive paragraph
    with st.container(): # Utilize st.container() as explained before
        # Combine all text into a single string to put inside the new box.
        combined_description = """
        <p class="solution-text">이 짧은 경험을 통해 느꼈듯이, 디지털 격차는 누군가에게는 <strong>거대한 장벽</strong>일 수 있음을 기억해야 합니다.</p>
        <p class="solution-text">밑의 그래프는 오늘 알아본 노인층과 외국인 층의 디지털 사용 현황입니다. 이를 통해, 아직 수많은 사람들이 디지털 사용이라는 장벽에 막혀 있음을 알 수 있죠. </p>
        <p class="solution-text">진정한 디지털 포용은 단순히 기술의 제공을 넘어, 모든 이가 소외되지 않고, 소통하며 성장할 수 있는 환경에서 시작됩니다. <strong>관심과 배려</strong>로 디지털 세상의 문턱을 낮춰나갈 때, 비로소 모두를 위한 따뜻한 연결을 이룰 수 있습니다.</p>
        """
        # Combine HTML tags and content into a single markdown string.
        st.markdown(f"""
        <div class="section-description-box">
            {combined_description}
        </div>
        """, unsafe_allow_html=True)

    # 2. Add <현황 그래프> title above the charts (h2 size)
    st.markdown('<h3 class="section-title">현황 그래프</h3>', unsafe_allow_html=True) # Add new class

    # Keep chart container
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)

    fig1, fig2 = create_digital_divide_charts() # Keep existing function call

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(fig1, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<h3>\"디지털 포용. 그것은 관심과 배려에서 시작됩니다.\"</h3>', unsafe_allow_html=True)


    st.markdown('<div style="margin-top: 30px;">', unsafe_allow_html=True)
    if st.button("처음으로 돌아가기", key="restart_button_page4"):
        st.session_state.current_page = 0
        st.session_state.selected_role = ''
        st.session_state.start_time = 0
        st.session_state.end_time = 0
        st.session_state.name = ''
        st.session_state.address = ''
        st.session_state.checkboxes = {
            'check1_elderly': False, 'check2_elderly': False, 'check3_elderly': False,
            'check1_foreigner': False, 'check2_foreigner': False, 'check3_foreigner': False,
        }
        st.session_state.ai_report_content = None
        # Check if set_page function exists, then call it
        if 'set_page' in globals():
            set_page(0)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)