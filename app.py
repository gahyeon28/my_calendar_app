import streamlit as st
from datetime import date, datetime
import calendar
import json
import os

# --- 1. 기본 설정 및 색상 팔레트 ---
st.set_page_config(page_title="My Scheduler", page_icon="📅", layout="centered")
DB_FILE = "calendar_tasks.json"

# 점(Dot)과 일정 띠지(Bar)에 공통으로 사용될 색상 저장소
COLOR_MAP = {
    "파랑": "#3182F6",
    "빨강": "#FF4B4B",
    "초록": "#00C853",
    "보라": "#A55EEA"
}

# 데이터 로드/저장 함수
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# 세션 상태 초기화
if 'tasks' not in st.session_state: st.session_state.tasks = load_data()
if 'selected_date' not in st.session_state: st.session_state.selected_date = date.today().strftime("%Y-%m-%d")
if 'view_year' not in st.session_state: st.session_state.view_year = date.today().year
if 'view_month' not in st.session_state: st.session_state.view_month = date.today().month

def move_month(delta):
    new_month = st.session_state.view_month + delta
    if new_month > 12: st.session_state.view_month = 1; st.session_state.view_year += 1
    elif new_month < 1: st.session_state.view_month = 12; st.session_state.view_year -= 1
    else: st.session_state.view_month = new_month

# --- 2. 강력한 커스텀 CSS (디자인 및 정렬) ---
st.markdown(f"""
    <style>
    /* 전체 배경 및 폰트 */
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: #FFFFFF !important; font-family: 'Apple SD Gothic Neo', sans-serif; }}
    
    /* 모바일 여백 최적화 */
    .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}

    /* 캘린더 박스 디자인 */
    .calendar-container {{
        background-color: #111111 !important;
        padding: 15px 5px !important; border-radius: 20px !important;
        border: 1px solid #333333 !important; margin-bottom: 20px !important;
    }}

    /* [해결] 모바일 가로 7열 강제 유지 */
    [data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; }}
    [data-testid="column"] {{ width: 14.28% !important; flex: 1 1 14.28% !important; min-width: 0 !important; }}

    /* 날짜 셀 정렬 */
    .day-cell {{ display: flex !important; flex-direction: column !important; align-items: center !important; height: 60px !important; position: relative !important; }}
    
    /* 원형 버튼 스타일 */
    [data-testid="stButton"] > button {{
        background-color: transparent !important; color: #FFFFFF !important; border: none !important; 
        width: 36px !important; height: 36px !important; border-radius: 50% !important; margin: 0 auto !important;
        padding: 0 !important; font-size: 16px !important;
    }}

    /* 빨간 원(오늘) 및 흰색 원(선택) */
    .is-today [data-testid="stButton"] > button {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .is-selected [data-testid="stButton"] > button {{ background-color: #FFFFFF !important; color: #000000 !important; }}

    /* 점(Dot) 중앙 정렬 및 크기 */
    .dot-row {{ display: flex !important; justify-content: center !important; gap: 3px !important; width: 100% !important; margin-top: 2px !important; }}
    .event-dot {{ width: 7px !important; height: 7px !important; border-radius: 50% !important; }}
    .dot-파랑 {{ background-color: {COLOR_MAP['파랑']} !important; }}
    .dot-빨강 {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .dot-초록 {{ background-color: {COLOR_MAP['초록']} !important; }}
    .dot-보라 {{ background-color: {COLOR_MAP['보라']} !important; }}
    
    /* 일정 카드: 왼쪽 띠지(border-left)는 데이터 색상과 연동됨 */
    .schedule-card {{
        background-color: #1A1A1A !important; padding: 12px 18px !important;
        border-radius: 15px !important; margin-bottom: 10px !important;
        display: flex; flex-direction: column;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI 구현 (타이틀 및 네비게이션) ---
st.markdown('<div style="text-align:center; font-size:22px; font-weight:800; margin-bottom:15px;">나의 스케줄러</div>', unsafe_allow_html=True)

nav = st.columns([1, 2, 1, 1])
with nav[0]: 
    if st.button("◀", key="m_prev"): move_month(-1); st.rerun()
with nav[1]: 
    st.markdown(f'<div style="text-align:center; font-weight:700; font-size:16px; padding-top:5px;">{st.session_state.view_month}월</div>', unsafe_allow_html=True)
with nav[2]: 
    if st.button("▶", key="m_next"): move_month(1); st.rerun()
with nav[3]:
    with st.popover("➕"):
        t_title = st.text_input("제목")
        t_cat = st.selectbox("분류", list(COLOR_MAP.keys()))
        t_date = st.date_input("날짜", value=date.today())
        t_hour = st.selectbox("시간", [f"{h:02d}:00" for h in range(24)], index=12)
        if st.button("저장"):
            st.session_state.tasks.append({"id": datetime.now().timestamp(), "title": t_title, "category": t_cat, "date": t_date.strftime("%Y-%m-%d"), "time": t_hour})
            save_data(st.session_state.tasks); st.rerun()

# 캘린더 그리드
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
cal_matrix = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)
today_str = date.today().strftime("%Y-%m-%d")

# 요일 헤더 표시
st.columns(7)
h_cols = st.columns(7)
for i, wd in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
    color = COLOR_MAP['빨강'] if i == 0 else (COLOR_MAP['파랑'] if i == 6 else "#888888")
    h_cols[i].markdown(f'<div style="text-align:center; font-size:11px; font-weight:700; color:{color};">{wd}</div>', unsafe_allow_html=True)

# 날짜 버튼 출력
for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day != 0:
                d_str = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{day:02d}"
                day_tasks = [t for t in st.session_state.tasks if t['date'] == d_str]
                state_cls = "is-today" if d_str == today_str else ""
                if d_str == st.session_state.selected_date: state_cls += " is-selected"
                
                st.markdown(f'<div class="day-cell {state_cls}">', unsafe_allow_html=True)
                if st.button(str(day), key=f"btn_{d_str}"):
                    st.session_state.selected_date = d_str; st.rerun()
                if day_tasks:
                    st.markdown('<div class="dot-row">', unsafe_allow_html=True)
                    for t in day_tasks[:2]: # 최대 2개 점 표시
                        st.markdown(f'<div class="event-dot dot-{t.get("category", "파랑")}"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 일정 목록 표시 (색상 연동의 핵심) ---
sel = st.session_state.selected_date
display_tasks = [t for t in st.session_state.tasks if t['date'] == sel]
st.markdown(f"#### {sel.split('-')[1]}월 {sel.split('-')[2]}일 일정")

for task in display_tasks:
    # 데이터에 저장된 카테고리를 이용해 띠지 색상 결정
    this_cat_color = COLOR_MAP.get(task.get('category', '파랑'), "#3182F6")
    st.markdown(f"""
        <div class="schedule-card" style="border-left: 6px solid {this_cat_color} !important;">
            <div style="color: {this_cat_color}; font-weight: 800; font-size: 13px;">{task['time']}</div>
            <div style="font-size: 16px; font-weight: 600;">{task['title']}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("삭제", key=f"del_{task['id']}"):
        st.session_state.tasks = [t for t in st.session_state.tasks if t.get('id') != task['id']]
        save_data(st.session_state.tasks); st.rerun()
