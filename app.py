import streamlit as st
from datetime import date, datetime
import calendar
import json
import os

# --- 1. 페이지 및 데이터 설정 ---
st.set_page_config(page_title="Pro Scheduler", page_icon="📅", layout="centered")
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
    st.session_state.selected_date = "2026-01-20" # 레퍼런스 기준 날짜
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

# --- 2. 강력한 CSS: 모바일 7열 고정 및 레퍼런스 디자인 ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: #FFFFFF !important; font-family: 'Apple SD Gothic Neo', sans-serif; }}

    /* 상단 타이틀 및 여백 */
    .block-container {{ padding-top: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
    .main-header {{ font-size: 24px; font-weight: 800; text-align: center; margin-bottom: 20px; }}

    /* [해결] 모바일 가로 7열 강제 유지 */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }}
    [data-testid="column"] {{
        width: 14.28% !important;
        flex: 1 1 14.28% !important;
        min-width: 0 !important;
    }}

    .calendar-container {{
        background-color: #111111 !important;
        padding: 15px 5px !important; border-radius: 20px !important;
        border: 1px solid #333333 !important; margin-bottom: 20px !important;
    }}

    /* 날짜 셀 정렬 및 높이 고정 */
    .day-cell {{
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        height: 65px !important; position: relative !important;
    }}

    /* 원형 버튼 스타일 */
    [data-testid="stButton"] > button {{
        background-color: transparent !important; color: #FFFFFF !important;
        border: none !important; width: 38px !important; height: 38px !important; 
        font-size: 16px !important; border-radius: 50% !important;
        padding: 0 !important; display: flex !important; align-items: center !important;
        justify-content: center !important; margin: 0 auto !important;
    }}

    /* [레퍼런스] 오늘 날짜: 빨간 원형 배경 */
    .is-today [data-testid="stButton"] > button {{
        background-color: {COLOR_MAP['빨강']} !important; color: #FFFFFF !important; font-weight: 800 !important;
    }}

    /* [레퍼런스] 선택된 날짜: 흰색 원형 배경 */
    .is-selected [data-testid="stButton"] > button {{
        background-color: #FFFFFF !important; color: #000000 !important; font-weight: 800 !important;
    }}

    /* [레퍼런스] 점(Dot) 정렬: 숫자 바로 아래 중앙 */
    .dot-row {{
        display: flex !important; justify-content: center !important;
        gap: 3px !important; width: 100% !important; height: 8px !important;
        margin-top: 2px !important;
    }}
    .event-dot {{ width: 6px !important; height: 6px !important; border-radius: 50% !important; }}
    .dot-파랑 {{ background-color: {COLOR_MAP['파랑']} !important; }}
    .dot-빨강 {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .dot-초록 {{ background-color: {COLOR_MAP['초록']} !important; }}
    .dot-보라 {{ background-color: {COLOR_MAP['보라']} !important; }}
    
    /* 일정 목록 카드 왼쪽 세로 줄 */
    .schedule-card {{
        background-color: #1A1A1A !important; padding: 12px 18px !important;
        border-radius: 15px !important; margin-bottom: 10px !important;
        display: flex; flex-direction: column;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 상단 UI ---
st.markdown('<div class="main-header">나의 스케줄러</div>', unsafe_allow_html=True)

nav = st.columns([1, 2, 1, 1])
with nav[0]: 
    if st.button("◀", key="m_prev"): move_month(-1); st.rerun()
with nav[1]: 
    st.markdown(f'<div style="text-align:center; font-weight:700; font-size:18px; padding-top:5px;">{st.session_state.view_month}월</div>', unsafe_allow_html=True)
with nav[2]: 
    if st.button("▶", key="m_next"): move_month(1); st.rerun()
with nav[3]:
    with st.popover("➕"):
        t_title = st.text_input("제목")
        t_cat = st.selectbox("분류", list(COLOR_MAP.keys()))
        t_date = st.date_input("날짜", value=date(2026, 1, 20))
        t_hour = st.selectbox("시간", [f"{h:02d}:00" for h in range(24)], index=12)
        if st.button("저장", use_container_width=True):
            if t_title:
                st.session_state.tasks.append({
                    "id": str(datetime.now().timestamp()),
                    "title": t_title, "category": t_cat,
                    "date": t_date.strftime("%Y-%m-%d"), "time": t_hour
                })
                save_data(st.session_state.tasks); st.rerun()

# --- 4. 캘린더 그리드 ---
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
cal_matrix = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)
today_str = date.today().strftime("%Y-%m-%d")

# 요일 표시
h_cols = st.columns(7)
for i, wd in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
    color = COLOR_MAP['빨강'] if i == 0 else (COLOR_MAP['파랑'] if i == 6 else "#888888")
    h_cols[i].markdown(f'<div style="text-align:center; font-size:12px; font-weight:700; color:{color};">{wd}</div>', unsafe_allow_html=True)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day != 0:
                d_str = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{day:02d}"
                day_tasks = [t for t in st.session_state.tasks if t['date'] == d_str]
                
                # 배경색 클래스 결정
                state_cls = ""
                if d_str == today_str: state_cls += " is-today"
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

# --- 5. 일정 목록 ---
sel = st.session_state.selected_date
display_tasks = [t for t in st.session_state.tasks if t['date'] == sel]
st.markdown(f"#### {sel.split('-')[1]}월 {sel.split('-')[2]}일 일정")

for task in display_tasks:
    this_cat_color = COLOR_MAP.get(task.get('category', '파랑'), "#3182F6")
    t_col, e_col, d_col = st.columns([5, 1, 1])
    with t_col:
        st.markdown(f"""
            <div class="schedule-card" style="border-left: 6px solid {this_cat_color} !important;">
                <div style="color: {this_cat_color}; font-weight: 800; font-size: 13px;">{task['time']}</div>
                <div style="font-size: 16px; font-weight: 600;">{task['title']}</div>
            </div>
        """, unsafe_allow_html=True)
    with e_col:
        with st.popover("📝"):
            u_title = st.text_input("제목", value=task['title'], key=f"u_t_{task['id']}")
            u_cat = st.selectbox("분류", list(COLOR_MAP.keys()), index=list(COLOR_MAP.keys()).index(task.get('category', '파랑')), key=f"u_c_{task['id']}")
            u_time = st.selectbox("시간", [f"{h:02d}:00" for h in range(24)], index=int(task['time'][:2]), key=f"u_h_{task['id']}")
            if st.button("수정 완료", key=f"u_b_{task['id']}", use_container_width=True):
                task.update({"title": u_title, "category": u_cat, "time": u_time})
                save_data(st.session_state.tasks); st.rerun()
    with d_col:
        if st.button("🗑️", key=f"del_{task['id']}"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t.get('id') != task['id']]
            save_data(st.session_state.tasks); st.rerun()
