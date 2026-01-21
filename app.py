import streamlit as st
from datetime import date, datetime
import calendar
import json
import os

# --- 1. 페이지 설정 및 데이터 관리 ---
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
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_data(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = "2026-01-20"
if 'view_year' not in st.session_state:
    st.session_state.view_year = 2026
if 'view_month' not in st.session_state:
    st.session_state.view_month = 1

def move_month(delta):
    new_month = st.session_state.view_month + delta
    if new_month > 12:
        st.session_state.view_month = 1; st.session_state.view_year += 1
    elif new_month < 1:
        st.session_state.view_month = 12; st.session_state.view_year -= 1
    else:
        st.session_state.view_month = new_month

# --- 2. CSS: 세로 길이 압축 및 한 화면 고정 ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: #FFFFFF !important; font-family: 'Apple SD Gothic Neo', sans-serif; }}

    /* [수정] 상단 여백 최소화 */
    .block-container {{ 
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important;
    }}
    
    .main-header {{ 
        font-size: 22px; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 10px;
    }}

    /* 모바일 가로 7열 강제 유지 */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }}
    [data-testid="column"] {{
        width: 14.28% !important;
        flex: 1 1 14.28% !important;
        min-width: 14.28% !important;
    }}

    /* 캘린더 컨테이너 여백 축소 */
    .calendar-container {{
        background-color: #111111 !important;
        padding: 10px 0px !important; 
        border-radius: 20px !important;
        border: 1px solid #333333 !important; 
        margin-bottom: 15px !important;
    }}

    .weekday-header div {{ color: #888888 !important; font-weight: 700; font-size: 11px; text-align: center; }}
    
    /* [수정] 날짜 셀 높이 대폭 압축 (75px -> 52px) */
    .day-cell {{
        display: flex !important; 
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: center !important;
        height: 52px !important; 
        position: relative !important;
    }}

    /* 버튼 크기 최적화 */
    [data-testid="stButton"] > button {{
        background-color: transparent !important; 
        color: #FFFFFF !important;
        border: none !important; 
        width: 34px !important; 
        height: 34px !important; 
        font-size: 15px !important; 
        border-radius: 50% !important;
        padding: 0 !important; 
        margin: 0 auto !important;
    }}

    .is-today [data-testid="stButton"] > button {{
        background-color: #FF4B4B !important; 
        color: #FFFFFF !important;
    }}

    .is-selected [data-testid="stButton"] > button {{
        background-color: #FFFFFF !important; 
        color: #000000 !important;
    }}

    /* 점(Dot) 위치를 숫자와 더 밀착 */
    .dot-row {{
        display: flex !important; 
        justify-content: center !important; 
        gap: 2px !important; 
        width: 100% !important; 
        margin-top: -2px !important;
    }}
    .event-dot {{ 
        width: 6px !important; 
        height: 6px !important; 
        border-radius: 50% !important; 
    }}
    .dot-파랑 {{ background-color: {COLOR_MAP['파랑']} !important; }}
    .dot-빨강 {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .dot-초록 {{ background-color: {COLOR_MAP['초록']} !important; }}
    .dot-보라 {{ background-color: {COLOR_MAP['보라']} !important; }}
    
    /* 일정 카드 여백 축소 */
    .schedule-card {{
        background-color: #1A1A1A !important; 
        padding: 10px 15px !important;
        border-radius: 12px !important; 
        margin-bottom: 8px !important;
        border-left: 5px solid #3182F6 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 상단 UI ---
st.markdown('<div class="main-header">스케줄러</div>', unsafe_allow_html=True)

nav_cols = st.columns([1, 2, 1, 1])
with nav_cols[0]:
    if st.button("◀", key="m_prev"): move_month(-1); st.rerun()
with nav_cols[1]:
    st.markdown(f'<div style="text-align:center; font-weight:700; padding-top:5px;">{st.session_state.view_month}월</div>', unsafe_allow_html=True)
with nav_cols[2]:
    if st.button("▶", key="m_next"): move_month(1); st.rerun()
with nav_cols[3]:
    with st.popover("➕"):
        t_title = st.text_input("제목")
        t_cat = st.selectbox("분류", list(COLOR_MAP.keys()))
        t_date = st.date_input("날짜", value=date(2026, 1, 20))
        t_hour = st.selectbox("시간", [f"{h:02d}:00" for h in range(24)], index=12)
        if st.button("저장"):
            if t_title:
                st.session_state.tasks.append({
                    "id": datetime.now().timestamp(), "title": t_title, "category": t_cat,
                    "date": t_date.strftime("%Y-%m-%d"), "time": t_hour
                })
                save_data(st.session_state.tasks); st.rerun()

# --- 4. 캘린더 그리드 (압축형) ---
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)

# 요일 표시
cols_h = st.columns(7)
for i, wd in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
    color = "#FF4B4B" if i == 0 else ("#3182F6" if i == 6 else "#888888")
    cols_h[i].markdown(f'<div class="weekday-header" style="color:{color} !important;">{wd}</div>', unsafe_allow_html=True)

today_str = "2026-01-20"
cal_matrix = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day != 0:
                d_str = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{day:02d}"
                is_selected = (d_str == st.session_state.selected_date)
                is_today = (d_str == today_str)
                day_tasks = [t for t in st.session_state.tasks if t['date'] == d_str]
                
                state_cls = ""
                if is_today: state_cls += " is-today"
                if is_selected: state_cls += " is-selected"
                
                st.markdown(f'<div class="day-cell {state_cls}">', unsafe_allow_html=True)
                if st.button(str(day), key=f"btn_{d_str}"):
                    st.session_state.selected_date = d_str
                    st.rerun()
                
                if day_tasks:
                    st.markdown('<div class="dot-row">', unsafe_allow_html=True)
                    for t in day_tasks[:2]:
                        st.markdown(f'<div class="event-dot dot-{t.get("category", "파랑")}"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 일정 목록 (콤팩트 카드) ---
sel = st.session_state.selected_date
display_tasks = [t for t in st.session_state.tasks if t['date'] == sel]
st.markdown(f'<div style="font-size:15px; font-weight:700; margin-bottom:10px;">{sel.split("-")[1]}월 {sel.split("-")[2]}일</div>', unsafe_allow_html=True)

if not display_tasks:
    st.markdown('<div style="color:#666; font-size:13px;">일정이 없습니다.</div>', unsafe_allow_html=True)
else:
    for task in display_tasks:
        cat_color = COLOR_MAP.get(task.get('category', '파랑'), "#3182F6")
        st.markdown(f"""
            <div class="schedule-card" style="border-left: 5px solid {cat_color};">
                <div style="color: {cat_color}; font-weight: 700; font-size: 12px;">{task['time']}</div>
                <div style="font-size: 14px; font-weight: 600;">{task['title']}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("삭제", key=f"del_{task['id']}", help="삭제"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t.get('id') != task['id']]
            save_data(st.session_state.tasks); st.rerun()
