import streamlit as st
from datetime import date, datetime
import calendar
import json
import os

# --- 1. 페이지 설정 및 데이터 관리 ---
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
    st.session_state.selected_date = "2026-01-20"
if 'view_year' not in st.session_state:
    st.session_state.view_year = 2026
if 'view_month' not in st.session_state:
    st.session_state.view_month = 1

def move_month(delta):
    new_month = st.session_state.view_month + delta
    if new_month > 12:
        st.session_state.view_month = 1
        st.session_state.view_year += 1
    elif new_month < 1:
        st.session_state.view_month = 12
        st.session_state.view_year -= 1
    else:
        st.session_state.view_month = new_month

# --- 2. CSS: 글자 짤림 방지 및 레퍼런스 디자인 적용 ---
st.markdown(f"""
    <style>
    /* 배경 설정 */
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: #FFFFFF !important; font-family: 'Apple SD Gothic Neo', sans-serif; }}

    /* [해결] 글자 짤림 방지: 상단 여백을 충분히 확보 */
    .block-container {{ 
        padding-top: 4rem !important; 
        padding-bottom: 2rem !important;
    }}
    
    .main-header {{ 
        font-size: 28px; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 10px;
        line-height: 1.4;
    }}

    /* 캘린더 컨테이너 */
    .calendar-container {{
        background-color: #111111 !important;
        padding: 20px 10px !important; 
        border-radius: 25px !important;
        border: 1px solid #333333 !important; 
        margin-bottom: 30px !important;
    }}

    .weekday-header div {{ color: #888888 !important; font-weight: 700; font-size: 13px; text-align: center; }}
    
    /* [해결] 날짜 셀: 고정 높이와 중앙 정렬 보장 */
    .day-cell {{
        display: flex !important; 
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: flex-start !important;
        height: 85px !important; 
        position: relative !important;
    }}

    /* 버튼 스타일: 원형 배경 고정 */
    [data-testid="stButton"] > button {{
        background-color: transparent !important; 
        color: #FFFFFF !important;
        border: none !important; 
        width: 44px !important; 
        height: 44px !important; 
        font-size: 18px !important; 
        border-radius: 50% !important;
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important; 
        margin: 0 auto !important; 
        padding: 0 !important;
    }}

    /* 오늘 날짜: 빨간 원 */
    .is-today [data-testid="stButton"] > button {{
        background-color: #FF4B4B !important; 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
    }}

    /* 선택된 날짜: 흰색 원 */
    .is-selected [data-testid="stButton"] > button {{
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-weight: 800 !important;
    }}

    /* 오늘이면서 선택됨 */
    .is-today.is-selected [data-testid="stButton"] > button {{
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        border: 4px solid #FF4B4B !important;
    }}

    /* [해결] 점(Dot) 정렬: 숫자 바로 아래 정중앙 배치 */
    .dot-row {{
        display: flex !important; 
        justify-content: center !important; 
        gap: 4px !important; 
        width: 100% !important; 
        margin-top: 4px !important;
    }}
    .event-dot {{ 
        width: 8px !important; 
        height: 8px !important; 
        border-radius: 50% !important; 
    }}
    .dot-파랑 {{ background-color: {COLOR_MAP['파랑']} !important; }}
    .dot-빨강 {{ background-color: {COLOR_MAP['빨강']} !important; }}
    .dot-초록 {{ background-color: {COLOR_MAP['초록']} !important; }}
    .dot-보라 {{ background-color: {COLOR_MAP['보라']} !important; }}
    
    /* 일정 목록 카드 왼쪽 세로 줄 */
    .schedule-card {{
        background-color: #1A1A1A !important; 
        padding: 15px 20px !important;
        border-radius: 18px !important; 
        margin-bottom: 12px !important;
        border-left: 7px solid #3182F6 !important;
        display: flex;
        flex-direction: column;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI 레이아웃 ---
st.markdown('<div class="main-header">스케줄러</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
with c1:
    if st.button("◀", key="m_prev"): move_month(-1); st.rerun()
with c2:
    st.markdown(f'<h3 style="text-align:center; margin:0; line-height:1.2;">{st.session_state.view_year}년 {st.session_state.view_month}월</h3>', unsafe_allow_html=True)
with c3:
    if st.button("▶", key="m_next"): move_month(1); st.rerun()
with c4:
    with st.popover("➕"):
        st.write("### 일정 추가")
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

# --- 4. 캘린더 그리드 ---
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
st.markdown('<div style="display:flex; justify-content:space-between; margin-bottom:18px; padding: 0 10px;">'
            '<div class="weekday-header" style="width:14%; color:#FF4B4B !important;">일</div>'
            '<div class="weekday-header" style="width:14%;">월</div><div class="weekday-header" style="width:14%;">화</div>'
            '<div class="weekday-header" style="width:14%;">수</div><div class="weekday-header" style="width:14%;">목</div>'
            '<div class="weekday-header" style="width:14%;">금</div>'
            '<div class="weekday-header" style="width:14%; color:#3182F6 !important;">토</div></div>', unsafe_allow_html=True)

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
                
                # 점(Dot) 중앙 정렬
                if day_tasks:
                    st.markdown('<div class="dot-row">', unsafe_allow_html=True)
                    for t in day_tasks[:2]:
                        st.markdown(f'<div class="event-dot dot-{t.get("category", "파랑")}"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="dot-row" style="height:10px;"></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 일정 목록 ---
sel = st.session_state.selected_date
display_tasks = [t for t in st.session_state.tasks if t['date'] == sel]
st.markdown(f"#### {sel.split('-')[1]}월 {sel.split('-')[2]}일 일정")

if not display_tasks:
    st.info("이날은 예정된 일정이 없습니다.")
else:
    for task in display_tasks:
        cat_color = COLOR_MAP.get(task.get('category', '파랑'), "#3182F6")
        st.markdown(f"""
            <div class="schedule-card" style="border-left: 7px solid {cat_color};">
                <div style="color: {cat_color}; font-weight: 800; font-size: 14px; margin-bottom: 2px;">{task['time']}</div>
                <div style="font-size: 17px; font-weight: 600;">{task['title']}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("삭제", key=f"del_{task['id']}"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t.get('id') != task['id']]
            save_data(st.session_state.tasks); st.rerun()