import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Импорт наших модулей
from import_ru import download_by_tnved, mark_friendly
from calc_import_metrics import calc_import_metrics
from draw_image import summarize_trends, pie_friendly_unfriendly_with_china

# Функции для создания графиков
def create_pie_chart(df_year, year):
    """Создает круговую диаграмму для конкретного года"""
    CHINA = 'China'
    
    # Подготовка данных
    d = df_year.copy()
    d['primaryValue'] = pd.to_numeric(d['primaryValue'], errors="coerce").fillna(0)
    
    # Маски
    mask_china = d['reporterDesc'].str.contains(CHINA, na=False)
    mask_friend = d['isFriendly'] == 1
    
    # Суммы по категориям
    val_china = float(d.loc[mask_china, 'primaryValue'].sum())
    val_friend_other = float(d.loc[mask_friend & ~mask_china, 'primaryValue'].sum())
    val_unfriendly = float(d.loc[~mask_friend, 'primaryValue'].sum())
    
    # Создание графика
    labels = ["Китай", "Другие дружественные", "Недружественные"]
    values = [val_china, val_friend_other, val_unfriendly]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent+value',
        textfont_size=14,
        marker_line=dict(color='white', width=2)
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Структура импорта по стоимости, {year}",
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12),
        showlegend=True,
        height=450,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def create_total_pie_chart(df1, df2, df3):
    """Создает общую круговую диаграмму за все годы"""
    CHINA = 'China'
    
    # Объединяем все данные
    df_total = pd.concat([df1, df2, df3], ignore_index=True)
    df_total['primaryValue'] = pd.to_numeric(df_total['primaryValue'], errors="coerce").fillna(0)
    
    # Маски
    mask_china = df_total['reporterDesc'].str.contains(CHINA, na=False)
    mask_friend = df_total['isFriendly'] == 1
    
    # Суммы по категориям
    val_china = float(df_total.loc[mask_china, 'primaryValue'].sum())
    val_friend_other = float(df_total.loc[mask_friend & ~mask_china, 'primaryValue'].sum())
    val_unfriendly = float(df_total.loc[~mask_friend, 'primaryValue'].sum())
    
    # Создание графика
    labels = ["Китай", "Другие дружественные", "Недружественные"]
    values = [val_china, val_friend_other, val_unfriendly]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent+value',
        textfont_size=16,
        marker_line=dict(color='white', width=3)
    )])
    
    fig.update_layout(
        title=dict(
            text="Общая структура импорта за 3 года",
            font=dict(size=18, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=14),
        showlegend=True,
        height=550,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def create_trend_chart(years, values, title, emoji):
    """Создает график тренда"""
    fig = go.Figure()
    
    # Определяем цвет в зависимости от типа графика
    if "импорт" in title.lower():
        color = '#1f77b4'
        gradient_color = 'rgba(31, 119, 180, 0.2)'
    elif "недружественных" in title.lower():
        color = '#FF6B6B'
        gradient_color = 'rgba(255, 107, 107, 0.2)'
    elif "китая" in title.lower():
        color = '#4ECDC4'
        gradient_color = 'rgba(78, 205, 196, 0.2)'
    else:
        color = '#45B7D1'
        gradient_color = 'rgba(69, 183, 209, 0.2)'
    
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=4, shape='spline'),
        marker=dict(
            size=12, 
            color=color,
            line=dict(color='white', width=2)
        ),
        fill='tonexty',
        fillcolor=gradient_color,
        hovertemplate=f'<b>{emoji} {title}</b><br>Год: %{{x}}<br>Значение: %{{y}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{emoji} {title}",
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text="Год", font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=dict(text=title, font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        font=dict(size=12),
        height=450,
        hovermode='x unified',
        showlegend=False
    )
    
    # Добавляем аннотации с значениями
    for i, (year, value) in enumerate(zip(years, values)):
        fig.add_annotation(
            x=year,
            y=value,
            text=f"<b>{value:.1f}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=color,
            ax=0,
            ay=-40,
            font=dict(size=12, color=color),
            bgcolor='white',
            bordercolor=color,
            borderwidth=1
        )
    
    return fig

# Настройка страницы
st.set_page_config(
    page_title="Анализ импорта РФ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Минимальные стили только для вкладок
st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        color: #262730;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("📊 Анализ импорта Российской Федерации")

# Боковая панель для ввода данных
with st.sidebar:
    st.markdown("### 🔧 Настройки анализа")
    
    # Ввод кода ТН ВЭД
    st.markdown("**Введите код ТН ВЭД:**")
    tnved_code = st.text_input(
        "Код ТН ВЭД", 
        value="842810", 
        help="Введите код товарной номенклатуры внешнеэкономической деятельности (например: 8528)"
    )
    
    # Кнопка для запуска анализа
    analyze_button = st.button("🚀 Запустить анализ", type="primary", use_container_width=True)
    
    # Информация о коде
    st.markdown("---")
    st.markdown("### ℹ️ Информация")
    st.info("""
    **Код 8528** - Мониторы и проекторы, не включенные в другие товарные позиции
    
    **Другие примеры:**
    - 8517 - Телефонные аппараты
    - 8471 - Автоматические машины для обработки данных
    - 8703 - Легковые автомобили
    """)

# Основной контент
if analyze_button:
    if not tnved_code or not tnved_code.isdigit():
        st.error("❌ Пожалуйста, введите корректный код ТН ВЭД (только цифры)")
    else:
        with st.spinner("🔄 Загружаем данные и выполняем анализ..."):
            try:
                # Загрузка данных
                df = download_by_tnved(tnved_code)
                df = mark_friendly(df)
                
                if df.empty:
                    st.error("❌ Данные по указанному коду ТН ВЭД не найдены")
                else:
                    # Подготовка данных
                    col = ['refYear', 'reporterDesc', 'isFriendly', 'primaryValue', 'qty', 'qtyUnitCode', 'netWgt','partnerDesc']
                    df_proc = df[col].copy()
                    
                    now = datetime.now()
                    years = [now.year - 3, now.year - 2, now.year - 1]  # [2021, 2022, 2023] - от старых к новым
                    
                    df_proc_year_1 = df_proc[df_proc['refYear'] == years[0]].sort_values(by='primaryValue', ascending=False).copy()  # 2021
                    df_proc_year_2 = df_proc[df_proc['refYear'] == years[1]].sort_values(by='primaryValue', ascending=False).copy()  # 2022
                    df_proc_year_3 = df_proc[df_proc['refYear'] == years[2]].sort_values(by='primaryValue', ascending=False).copy()  # 2023
                    
                    # Расчет метрик в правильном порядке (от старых к новым)
                    records = []
                    records.append(calc_import_metrics(df_proc_year_1))  # 2021
                    records.append(calc_import_metrics(df_proc_year_2))  # 2022
                    records.append(calc_import_metrics(df_proc_year_3))  # 2023
                    
                    # Анализ трендов
                    res = summarize_trends(records, plot=False)
                    
                    # Сохранение данных в session state
                    st.session_state.df_proc_year_1 = df_proc_year_1
                    st.session_state.df_proc_year_2 = df_proc_year_2
                    st.session_state.df_proc_year_3 = df_proc_year_3
                    st.session_state.records = records
                    st.session_state.trends = res
                    st.session_state.tnved_code = tnved_code
                    st.session_state.years = years  # Сохраняем годы для отображения
                    
                    st.success(f"✅ Анализ успешно выполнен для кода ТН ВЭД: {tnved_code}")
                    st.info(f"📅 Анализируемые годы: {years[0]}, {years[1]}, {years[2]}")
                    
            except Exception as e:
                st.error(f"❌ Ошибка при выполнении анализа: {str(e)}")

# Отображение результатов
if 'trends' in st.session_state:
    # Создание вкладок
    tab1, tab2 = st.tabs(["📈 Обзор", "📊 Анализ импорта РФ"])
    
    with tab1:
        st.header("📋 Краткий обзор")
        st.divider()
        
        # Основные метрики
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_import = st.session_state.records[-1]['import_total']
            st.metric(
                label="💰 Общий импорт (последний год)",
                value=f"{total_import:,.0f} $".replace(",", " "),
                delta=f"{st.session_state.trends['trends']['import_total']['delta_pct']*100:+.1f}%" if not np.isnan(st.session_state.trends['trends']['import_total']['delta_pct']) else "N/A"
            )
        
        with col2:
            share_unfriendly = st.session_state.records[-1]['share_unfriendly']
            st.metric(
                label="🚫 Доля недружественных стран",
                value=f"{share_unfriendly*100:.1f}%",
                delta=f"{st.session_state.trends['trends']['share_unfriendly']['delta_pct']*100:+.1f}%" if not np.isnan(st.session_state.trends['trends']['share_unfriendly']['delta_pct']) else "N/A"
            )
        
        with col3:
            share_china = st.session_state.records[-1]['share_china']
            st.metric(
                label="🇨🇳 Доля Китая",
                value=f"{share_china*100:.1f}%",
                delta=f"{st.session_state.trends['trends']['share_china']['delta_pct']*100:+.1f}%" if not np.isnan(st.session_state.trends['trends']['share_china']['delta_pct']) else "N/A"
            )
        
        with col4:
            price_ratio = st.session_state.records[-1]['price_diff_ratio']
            if not np.isnan(price_ratio):
                st.metric(
                    label="💱 Отношение цен (Китай/другие)",
                    value=f"{price_ratio:.2f}",
                    delta="Демпинг" if price_ratio < 1.0 else "Норма"
                )
            else:
                st.metric(
                    label="💱 Отношение цен",
                    value="N/A",
                    delta="Нет данных"
                )
        
        # Информация о трендах
        st.header("📈 Тренды за 3 года")
        st.divider()
        
        trends_data = []
        for key, trend in st.session_state.trends['trends'].items():
            trends_data.append({
                'Метрика': trend['title'],
                'Тренд': trend['label'],
                'Изменение (%)': f"{trend['delta_pct']*100:+.1f}%" if not np.isnan(trend['delta_pct']) else "N/A",
                'CAGR (%)': f"{trend['cagr']*100:+.1f}%" if not np.isnan(trend['cagr']) else "N/A"
            })
        
        trends_df = pd.DataFrame(trends_data)
        st.dataframe(trends_df, use_container_width=True)
        
        # Дополнительная информация
        st.info("💡 **Подсказка**: Положительный тренд означает рост показателя, отрицательный - снижение, стабильный - незначительные изменения.")
    
    with tab2:
        st.header("📊 Детальный анализ импорта РФ")
        st.info("📊 **Информация**: Графики показывают структуру импорта по странам и динамику ключевых показателей за последние 3 года.")
        st.divider()
        
        # Графики пирога по годам
        st.header("🥧 Структура импорта по годам")
        st.caption("Круговые диаграммы показывают долю каждой категории стран в общем объеме импорта")
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # График для первого года (2021)
            if not st.session_state.df_proc_year_1.empty:
                fig1 = create_pie_chart(st.session_state.df_proc_year_1, st.session_state.years[0])
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # График для второго года (2022)
            if not st.session_state.df_proc_year_2.empty:
                fig2 = create_pie_chart(st.session_state.df_proc_year_2, st.session_state.years[1])
                st.plotly_chart(fig2, use_container_width=True)
        
        # График для третьего года (2023)
        if not st.session_state.df_proc_year_3.empty:
            fig3 = create_pie_chart(st.session_state.df_proc_year_3, st.session_state.years[2])
            st.plotly_chart(fig3, use_container_width=True)
        
        # Общий график за все годы
        st.header("📊 Общая структура импорта за 3 года")
        st.caption("Сводная диаграмма показывает общую структуру импорта за весь анализируемый период")
        st.divider()
        fig_total = create_total_pie_chart(st.session_state.df_proc_year_1, st.session_state.df_proc_year_2, st.session_state.df_proc_year_3)
        st.plotly_chart(fig_total, use_container_width=True)
        
        # Графики трендов
        st.header("📈 Тренды по ключевым показателям")
        st.caption("Линейные графики показывают динамику изменения показателей во времени")
        st.divider()
        
        # График общего импорта
        fig_import = create_trend_chart(
            st.session_state.trends['years'],
            [r['import_total'] for r in st.session_state.records],
            "Общий импорт, $",
            "💰"
        )
        st.plotly_chart(fig_import, use_container_width=True)
        
        # График доли недружественных стран
        fig_unfriendly = create_trend_chart(
            st.session_state.trends['years'],
            [r['share_unfriendly']*100 for r in st.session_state.records],
            "Доля недружественных стран, %",
            "🚫"
        )
        st.plotly_chart(fig_unfriendly, use_container_width=True)
        
        # График доли Китая
        fig_china = create_trend_chart(
            st.session_state.trends['years'],
            [r['share_china']*100 for r in st.session_state.records],
            "Доля Китая, %",
            "🇨🇳"
        )
        st.plotly_chart(fig_china, use_container_width=True)

# Футер
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("📊 **Анализ импорта РФ** | Создано с помощью Streamlit")
    st.caption("Данные предоставлены UN Comtrade API")
