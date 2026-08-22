
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="HR Дашборд — Персонал",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS для темной темы и стилей
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e2e;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #cdd6f4;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #313244 !important;
        color: #89b4fa !important;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
    div[data-testid="stMetricDelta"] { font-size: 0.9rem; }
    .css-1r6slb0 { background-color: #1e1e2e; border-radius: 12px; padding: 1rem; }
    .stDataFrame { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(uploaded_file):
    """Загрузка и очистка данных из Excel"""
    df = pd.read_excel(uploaded_file, sheet_name='Данные', header=0)
    df.columns = ['№', 'Sicil', 'Adi Soyadi', 'Vatandaslik', 'Santiye', '№ Паспорта',
                  'Документ', 'Kamp girisi', 'MK', 'Ogretmen', 'Sinav',
                  'Egtim durumu', 'Shohruh Not', 'Дней в РФ']
    # Удаляем строку-дубль заголовков если есть
    df = df[df['№'] != '№'].copy()
    # Преобразуем типы
    df['Sicil'] = pd.to_numeric(df['Sicil'], errors='coerce')
    df['Дней в РФ'] = pd.to_numeric(df['Дней в РФ'], errors='coerce')
    df['№'] = pd.to_numeric(df['№'], errors='coerce')
    # Очистка пробелов
    for col in ['Vatandaslik', 'Santiye', 'Документ', 'Egtim durumu', 'Ogretmen']:
        df[col] = df[col].astype(str).str.strip()
    return df.reset_index(drop=True)

def get_metrics(df):
    """Расчет ключевых метрик"""
    total = len(df)
    passed = len(df[df['Egtim durumu'] == 'Dil egitimi tamamlandi sinavdan gecti'])
    failed_twice = len(df[df['Egtim durumu'] == '2 kere sinavden gecemedi'])
    ready = len(df[df['Egtim durumu'] == 'sinavi hazir'])
    studying = len(df[df['Egtim durumu'] == 'Egitime  devem eden'])
    to_study = len(df[df['Egtim durumu'] == 'Egitime alinacak'])
    return total, passed, failed_twice, ready, studying, to_study

def filter_df(df, obj, teacher, citizen):
    """Фильтрация по боковой панели"""
    d = df.copy()
    if obj != 'Все':
        d = d[d['Santiye'] == obj]
    if teacher != 'Все':
        d = d[d['Ogretmen'].str.contains(teacher, na=False)]
    if citizen != 'Все':
        d = d[d['Vatandaslik'] == citizen]
    return d

# ===== SIDEBAR =====
with st.sidebar:
    st.title("📁 Загрузка данных")
    uploaded_file = st.file_uploader(
        "Выберите Excel-файл (HR_Дашборд_персо.xlsx)",
        type=['xlsx', 'xls'],
        help="Загрузите файл — дашборд обновится автоматически"
    )

    st.markdown("---")
    st.markdown("### 🎛️ Фильтры")

    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)

        objects = ['Все'] + sorted(df_raw['Santiye'].dropna().unique().tolist())
        teachers = ['Все'] + sorted([t for t in df_raw['Ogretmen'].dropna().unique() if t != '-'])
        citizens = ['Все'] + sorted(df_raw['Vatandaslik'].dropna().unique().tolist())

        sel_obj = st.selectbox("Объект (Santiye)", objects)
        sel_teacher = st.selectbox("Учитель (Ogretmen)", teachers)
        sel_citizen = st.selectbox("Гражданство", citizens)

        st.markdown("---")
        st.info(f"📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        st.markdown("*Загрузите новый файл — данные обновятся автоматически*")
    else:
        st.warning("⬆️ Загрузите Excel-файл для начала работы")
        sel_obj = sel_teacher = sel_citizen = 'Все'
        df_raw = pd.DataFrame()

# ===== MAIN =====
st.title("📊 ОТЧЁТ ПО ПЕРСОНАЛУ — ОБУЧЕНИЕ И ОФОРМЛЕНИЕ ПАТЕНТОВ")

if uploaded_file is None:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; background: #1e1e2e; border-radius: 16px;">
        <h2 style="color: #89b4fa;">Добро пожаловать!</h2>
        <p style="font-size: 1.2rem; color: #cdd6f4;">
            Загрузите ваш Excel-файл через боковую панель слева.<br>
            Дашборд построится автоматически: графики, таблицы, поиск по сотрудникам.
        </p>
        <p style="color: #6c7086;">Поддерживаемый формат: .xlsx с листом «Данные»</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Применяем фильтры
df = filter_df(df_raw, sel_obj, sel_teacher, sel_citizen)
total, passed, failed_twice, ready, studying, to_study = get_metrics(df)

# KPI карточки
st.markdown("### 📈 Ключевые показатели")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("ВСЕГО", f"{total}", "сотрудников")
c2.metric("ЭКЗАМЕН СДАН", f"{passed}", f"{passed/total*100:.1f}%" if total else "0%")
c3.metric("НЕ СДАЛИ 2 РАЗА", f"{failed_twice}", f"{failed_twice/total*100:.1f}%" if total else "0%", delta_color="inverse")
c4.metric("ГОТОВЫ К ЭКЗАМЕНУ", f"{ready}")
c5.metric("ОБУЧЕНИЕ", f"{studying}")
c6.metric("К ОБУЧЕНИЮ", f"{to_study}")

st.markdown("---")

# Вкладки
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Дашборд", "❌ Не сдали", "⏳ В процессе", "✅ Готовы к экзамену",
    "📚 Обучение", "🎓 Экзамен сдан", "📝 К обучению", "🔍 Поиск"
])

# ===== TAB 1: ДАШБОРД =====
with tab1:
    st.markdown("### 📊 Распределение персонала")

    col_left, col_right = st.columns(2)

    with col_left:
        # Гражданство
        fig1 = px.pie(
            df['Vatandaslik'].value_counts().reset_index(),
            names='Vatandaslik', values='count',
            title="Гражданство",
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.45
        )
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4')
        st.plotly_chart(fig1, use_container_width=True)

        # Объект
        fig3 = px.bar(
            df['Santiye'].value_counts().reset_index(),
            x='Santiye', y='count',
            title="Объект (Santiye)",
            color='count', color_continuous_scale='Plasma'
        )
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4')
        st.plotly_chart(fig3, use_container_width=True)

    with col_right:
        # Тип документа
        doc_counts = df[df['Документ'] != '-']['Документ'].value_counts().reset_index()
        fig2 = px.pie(
            doc_counts,
            names='Документ', values='count',
            title="Тип документа",
            color_discrete_sequence=['#89b4fa', '#f38ba8'],
            hole=0.45
        )
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4')
        st.plotly_chart(fig2, use_container_width=True)

        # Статус обучения
        status_counts = df['Egtim durumu'].value_counts().reset_index()
        fig4 = px.bar(
            status_counts,
            x='count', y='Egtim durumu', orientation='h',
            title="Статус обучения / экзамена",
            color='count', color_continuous_scale='Plasma'
        )
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4', yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Полная таблица данных")
    st.dataframe(df, use_container_width=True, height=500)

# ===== TAB 2: НЕ СДАЛИ =====
with tab2:
    st.markdown(f"### ❌ Сотрудники: 2 раза не сдали экзамен — **{failed_twice}** записей")
    df_fail = df[df['Egtim durumu'] == '2 kere sinavden gecemedi']
    if len(df_fail):
        st.dataframe(df_fail[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.success("Нет сотрудников с двойным неудачным экзаменом в выборке")

# ===== TAB 3: В ПРОЦЕССЕ =====
with tab3:
    in_progress_statuses = ['Egitime  devem eden', 'Egitime alinacak', 'sinavi hazir']
    df_prog = df[df['Egtim durumu'].isin(in_progress_statuses)]
    st.markdown(f"### ⏳ Сотрудники в процессе обучения — **{len(df_prog)}** записей")
    if len(df_prog):
        st.dataframe(df_prog[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.info("Нет сотрудников в процессе в выборке")

# ===== TAB 4: ГОТОВЫ К ЭКЗАМЕНУ =====
with tab4:
    st.markdown(f"### ✅ Сотрудники, готовые к экзамену (sinavi hazir) — **{ready}** записей")
    df_ready = df[df['Egtim durumu'] == 'sinavi hazir']
    if len(df_ready):
        st.dataframe(df_ready[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.info("Нет сотрудников со статусом 'готов к экзамену'")

# ===== TAB 5: ОБУЧЕНИЕ =====
with tab5:
    st.markdown(f"### 📚 Сотрудники, продолжающие обучение — **{studying}** записей")
    df_study = df[df['Egtim durumu'] == 'Egitime  devem eden']
    if len(df_study):
        st.dataframe(df_study[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.info("Нет сотрудников на обучении")

# ===== TAB 6: ЭКЗАМЕН СДАН =====
with tab6:
    st.markdown(f"### 🎓 Сотрудники, сдавшие экзамен — **{passed}** записей")
    df_pass = df[df['Egtim durumu'] == 'Dil egitimi tamamlandi sinavdan gecti']
    if len(df_pass):
        st.dataframe(df_pass[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.info("Нет сотрудников со сданным экзаменом")

# ===== TAB 7: К ОБУЧЕНИЮ =====
with tab7:
    st.markdown(f"### 📝 Сотрудники, которых направят на обучение — **{to_study}** записей")
    df_tostudy = df[df['Egtim durumu'] == 'Egitime alinacak']
    if len(df_tostudy):
        st.dataframe(df_tostudy[['Sicil','Adi Soyadi','Vatandaslik','Santiye','Ogretmen','Sinav','Egtim durumu','Shohruh Not','Дней в РФ']], use_container_width=True)
    else:
        st.info("Нет сотрудников к обучению")

# ===== TAB 8: ПОИСК =====
with tab8:
    st.markdown("### 🔍 Поиск сотрудника по табельному номеру (Sicil)")
    search_sicil = st.text_input("Введите Sicil:", placeholder="например: 620941")

    if search_sicil:
        try:
            search_val = int(search_sicil)
            found = df_raw[df_raw['Sicil'] == search_val]
            if len(found):
                row = found.iloc[0]
                st.success(f"Сотрудник найден: **{row['Adi Soyadi']}**")

                cols = st.columns(2)
                info = [
                    ("Табельный №", row['Sicil']),
                    ("ФИО", row['Adi Soyadi']),
                    ("Гражданство", row['Vatandaslik']),
                    ("Объект", row['Santiye']),
                    ("№ Паспорта", row['№ Паспорта']),
                    ("Документ", row['Документ']),
                    ("Kamp girisi", row['Kamp girisi']),
                    ("MK (дата въезда)", row['MK']),
                    ("Дней в РФ", row['Дней в РФ']),
                    ("Учитель", row['Ogretmen']),
                    ("Экзамен (детали)", row['Sinav']),
                    ("Статус обучения", row['Egtim durumu']),
                    ("Примечание", row['Shohruh Not']),
                ]
                for i, (label, value) in enumerate(info):
                    with cols[i % 2]:
                        st.markdown(f"**{label}:** {value if pd.notna(value) else '-'}")
            else:
                st.error("Сотрудник не найден")
        except ValueError:
            st.error("Введите числовой табельный номер")
