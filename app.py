import streamlit as st
from datetime import date, datetime
import calendar
import json
import os

# --- 1. 기본 설정 및 색상 데이터 ---
st.set_page_config(page_title="My Scheduler", page_icon="📅", layout="centered")
DB_FILE = "calendar_tasks.json"

COLOR_MAP = {
    "파랑": "#3182F6",
    "빨강": "#FF4B4B",
    "초록": "#00C853",
    "보라": "#A55EEA"
}

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

if 'tasks' not in st.session_state: st.session_state.tasks = load_data()
if 'selected_date' not in st.session_state: st.session_state.selected_date = date.today().strftime("%Y-%m-%d")
if 'view_year' not in st.session_state: st.session_state.view_year = 2026
if 'view_month' not in st.session_state: st.session_state.view_month = 1

def move_month(delta):
    new_month = st.session_state.view_month + delta
    if new_month > 12: st.session_state.view_month = 1; st.session_state.view_year += 1
    elif new_month < 1: st.session_state.view_month = 12; st.session_state.view_year -= 1
    else: st.session_state.view_month = new_month

# --- 2. 강력한 CSS (가로폭 고정 + 띠지 복구) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: #FFFFFF !important; font-family: 'Apple SD Gothic Neo', sans-serif; }}
    
    /* [해결] 상단 글자 짤림 방지 및 가로 여백 최소화 */
    .block-container {{ 
        padding-top: 3.5rem !important; 
        padding-left: 0.3rem !important; 
        padding-right: 0.3rem !important; 
        max-width: 100% !important;
    }}

    /* [해결] 모바일 가로 7열 강제 유지 */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 1px !important;
    }}
    [data-testid="column"] {{
        width: 14.28% !important;
        flex: 1 1 14.28% !important;
        min-width: 0 !important;
    }}

    .calendar-container {{
        background-color: #111111 !important;
        padding: 10px 0px !important; 
        border-radius: 20px !important;
        border: 1px solid #333333 !important; 
        margin-bottom: 15px !important;
    }}

    /* 날짜 셀 높이 압축 */
    .day-cell {{
        display: flex !important; 
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: center !important;
        height: 52px !important; 
        position: relative !important;
    }}

    /* 원형 버튼 */
    [data-testid="stButton"] > button {{
        background-color: transparent !important; 
        color: #FFFFFF !important;
        border: none !important; 
        width: 32px !important; 
        height: 32px !important; 
        font-size: 14px !important; 
        border-radius: 50% !important;
        padding: 0 !important;
        margin: 0 auto !important;
    }}

    .is-today [data-testid="stButton"] > button {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .is-selected [data-testid="stButton"] > button {{ background-color: #FFFFFF !important; color: #000000 !important; }}

    /* 점(Dot) 정렬 */
    .dot-row {{ display: flex !important; justify-content: center !important; gap: 2px !important; width: 100% !important; margin-top: -1px !important; }}
    .event-dot {{ width: 7px !important; height: 7px !important; border-radius: 50% !important; }}
    .dot-파랑 {{ background-color: {COLOR_MAP['파랑']} !important; }}
    .dot-빨강 {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .dot-초록 {{ background-color: {COLOR_MAP['초록']} !important; }}
    .dot-보라 {{ background-color: {COLOR_MAP['보라']} !important; }}
    
    /* [해결] 일정 카드 디자인: 띠지 스타일 강화 */
    .schedule-card {{
        background-color: #1A1A1A !important; 
        padding: 12px 15px !important;
        border-radius: 12px !important; 
        margin-bottom: 10px !important;
        display: flex;
        flex-direction: column;
        border-top: none !important;
        border-right: none !important;
        border-bottom: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI 및 캘린더 ---
st.markdown('<div style="text-align:center; font-size:22px; font-weight:800; margin-bottom:10px;">스케줄러</div>', unsafe_allow_html=True)

nav = st.columns([1, 2, 1, 1])
with nav[0]: 
    if st.button("◀", key="m_prev"): move_month(-1); st.rerun()
with nav[1]: 
    st.markdown(f'<div style="text-align:center; font-weight:700; font-size:16px;">{st.session_state.view_month}월</div>', unsafe_allow_html=True)
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

st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
h_cols = st.columns(7)
for i, wd in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
    color = COLOR_MAP['빨강'] if i == 0 else (COLOR_MAP['파랑'] if i == 6 else "#888888")
    h_cols[i].markdown(f'<div style="text-align:center; font-size:10px; font-weight:700; color:{color};">{wd}</div>', unsafe_allow_html=True)

cal_matrix = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)
today_str = date.today().strftime("%Y-%m-%d")

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
                    for t in day_tasks[:2]:
                        st.markdown(f'<div class="event-dot dot-{t.get("category", "파랑")}"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 일정 목록 (띠지 색상 연동) ---
sel = st.session_state.selected_date
display_tasks = [t for t in st.session_state.tasks if t['date'] == sel]
st.markdown(f"#### {sel.split('-')[1]}월 {sel.split('-')[2]}일")

for task in display_tasks:
    # 점의 색상과 동일한 색상을 COLOR_MAP에서 가져와 띠지에 적용
    this_cat_color = COLOR_MAP.get(task.get('category', '파랑'), "#3182F6")
    st.markdown(f"""
        <div class="schedule-card" style="border-left: 6px solid {this_cat_color} !important;">
            <div style="color: {this_cat_color}; font-weight: 800; font-size: 13px;">{task['time']}</div>
            <div style="font-size: 15px; font-weight: 600;">{task['title']}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("삭제", key=f"del_{task['id']}"):
        st.session_state.tasks = [t for t in st.session_state.tasks if t.get('id') != task['id']]
        save_data(st.session_state.tasks); st.rerun()
