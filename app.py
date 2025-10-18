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
from calc_man_metrics import calculate_man_metrics, get_summary_metrics
from llm.llm_answer import get_llm_answer

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

def create_production_chart(years, production_data, consumption_data, title, category):
    """Создает график производства и потребления"""
    fig = go.Figure()
    
    # График производства
    fig.add_trace(go.Scatter(
        x=years,
        y=production_data,
        mode='lines+markers',
        name='Производство',
        line=dict(color='#2E8B57', width=4, shape='spline'),
        marker=dict(size=12, color='#2E8B57', line=dict(color='white', width=2)),
        fill='tonexty',
        fillcolor='rgba(46, 139, 87, 0.2)',
        hovertemplate=f'<b>🏭 Производство</b><br>Год: %{{x}}<br>Значение: %{{y}}<extra></extra>'
    ))
    
    # График потребления
    fig.add_trace(go.Scatter(
        x=years,
        y=consumption_data,
        mode='lines+markers',
        name='Потребление',
        line=dict(color='#FF6B6B', width=4, shape='spline'),
        marker=dict(size=12, color='#FF6B6B', line=dict(color='white', width=2)),
        fill='tonexty',
        fillcolor='rgba(255, 107, 107, 0.2)',
        hovertemplate=f'<b>🛒 Потребление</b><br>Год: %{{x}}<br>Значение: %{{y}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"🏭 {title} - {category}",
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
            title=dict(text="Объем", font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        font=dict(size=12),
        height=450,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_self_sufficiency_chart(years, self_sufficiency_data, title, category):
    """Создает график самообеспеченности"""
    fig = go.Figure()
    
    # Линия самообеспеченности
    fig.add_trace(go.Scatter(
        x=years,
        y=self_sufficiency_data,
        mode='lines+markers',
        name='Самообеспеченность',
        line=dict(color='#4ECDC4', width=4, shape='spline'),
        marker=dict(size=12, color='#4ECDC4', line=dict(color='white', width=2)),
        fill='tonexty',
        fillcolor='rgba(78, 205, 196, 0.2)',
        hovertemplate=f'<b>📊 Самообеспеченность</b><br>Год: %{{x}}<br>Значение: %{{y:.2f}}<extra></extra>'
    ))
    
    # Линия 100% самообеспеченности
    fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                  annotation_text="100% самообеспеченность", 
                  annotation_position="bottom right")
    
    fig.update_layout(
        title=dict(
            text=f"📊 {title} - {category}",
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
            title=dict(text="Коэффициент самообеспеченности", font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12),
            gridcolor='rgba(128,128,128,0.2)',
            range=[0, max(1.2, max(self_sufficiency_data) * 1.1)]
        ),
        font=dict(size=12),
        height=450,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_import_dependency_chart(years, import_dependency_data, title, category):
    """Создает график зависимости от импорта"""
    fig = go.Figure()
    
    # График зависимости от импорта
    fig.add_trace(go.Scatter(
        x=years,
        y=import_dependency_data,
        mode='lines+markers',
        name='Зависимость от импорта',
        line=dict(color='#FF8C00', width=4, shape='spline'),
        marker=dict(size=12, color='#FF8C00', line=dict(color='white', width=2)),
        fill='tonexty',
        fillcolor='rgba(255, 140, 0, 0.2)',
        hovertemplate=f'<b>📦 Зависимость от импорта</b><br>Год: %{{x}}<br>Значение: %{{y:.2f}}<extra></extra>'
    ))
    
    # Линия 30% зависимости (критический порог)
    fig.add_hline(y=0.3, line_dash="dash", line_color="red", 
                  annotation_text="Критический порог 30%", 
                  annotation_position="bottom right")
    
    fig.update_layout(
        title=dict(
            text=f"📦 {title} - {category}",
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
            title=dict(text="Коэффициент зависимости", font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12),
            gridcolor='rgba(128,128,128,0.2)',
            range=[0, max(0.5, max(import_dependency_data) * 1.1)]
        ),
        font=dict(size=12),
        height=450,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_metrics_radar_chart(metrics_data, category):
    """Создает радарную диаграмму метрик"""
    fig = go.Figure()
    
    # Подготавливаем данные для радара
    metrics = ['self_sufficiency', 'production_share', 'competitiveness_index', 'self_sufficiency_index']
    values = []
    labels = ['Самообеспеченность', 'Доля производства', 'Конкурентоспособность', 'Индекс самообеспеченности']
    
    for metric in metrics:
        if metric in metrics_data and metrics_data[metric] is not None:
            # Нормализуем значения для радара (0-1)
            if metric == 'competitiveness_index':
                # Для индекса конкурентоспособности используем логарифмическую шкалу
                value = min(1.0, np.log10(metrics_data[metric] + 1) / 3)
            else:
                value = min(1.0, metrics_data[metric])
            values.append(value)
        else:
            values.append(0)
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name=category,
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title=dict(
            text=f"📊 Радар метрик - {category}",
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        height=500
    )
    
    return fig

def format_metrics_for_llm():
    """Форматирует все метрики для передачи в LLM промпт"""
    if 'trends' not in st.session_state:
        return "Данные не загружены"
    
    latest_record = st.session_state.records[-1]
    trends = st.session_state.trends
    latest_year = st.session_state.years[-1]
    tnved_code = st.session_state.tnved_code
    
    # Формируем строку с метриками
    metrics_text = f"""
Данные:
Код ТН ВЭД: {tnved_code}
Период: {latest_year} год

Объём импорта (import_total): {latest_record['import_total']:,.0f}
Тренд импорта (import_total_trend): {trends['trends']['import_total']['label']}

Доля импорта из недружественных стран (share_unfriendly): {latest_record['share_unfriendly']:.3f}
Тренд доли НС (share_unfriendly_trend): {trends['trends']['share_unfriendly']['label']}

Доля импорта из Китая (share_china): {latest_record['share_china']:.3f}
Тренд доли Китая (share_china_trend): {trends['trends']['share_china']['label']}
"""
    
    # Добавляем ценовые метрики
    if not np.isnan(latest_record['price_china']):
        metrics_text += f"Средняя цена из Китая (price_china): {latest_record['price_china']:.2f}\n"
    else:
        metrics_text += "Средняя цена из Китая (price_china): N/A\n"
    
    if not np.isnan(latest_record['price_others']):
        metrics_text += f"Средняя цена из прочих стран (price_others): {latest_record['price_others']:.2f}\n"
    else:
        metrics_text += "Средняя цена из прочих стран (price_others): N/A\n"
    
    if not np.isnan(latest_record['price_diff_ratio']):
        metrics_text += f"Отношение цен (price_diff_ratio): {latest_record['price_diff_ratio']:.3f}\n"
        metrics_text += f"Флаг демпинга (dumping_flag): {latest_record['price_diff_ratio'] < 1.0}\n"
    else:
        metrics_text += "Отношение цен (price_diff_ratio): N/A\n"
        metrics_text += "Флаг демпинга (dumping_flag): N/A\n"
    
    # Добавляем флаги для мер ТТР
    metrics_text += "\nФлаги для мер ТТР:\n"
    for flag_key, flag_value in trends['flags'].items():
        metrics_text += f"{flag_key}: {flag_value}\n"
    
    # Добавляем метрики производства и потребления, если они доступны
    if 'production_metrics' in st.session_state:
        metrics_text += "\n=== МЕТРИКИ ПРОИЗВОДСТВА И ПОТРЕБЛЕНИЯ ===\n"
        
        for category, category_metrics in st.session_state.production_metrics.items():
            latest_year_prod = max(category_metrics.keys())
            latest_metrics = category_metrics[latest_year_prod]
            
            metrics_text += f"\nКатегория: {category}\n"
            metrics_text += f"Производство в России (production_total): {latest_metrics['manufacture']:,.0f}\n"
            metrics_text += f"Потребление в России (consumption_total): {latest_metrics['consumption']:,.0f}\n"
            metrics_text += f"Производство покрывает потребление: {latest_metrics['self_sufficiency'] >= 1.0}\n"
            
            if latest_metrics['growth_rate'] is not None:
                metrics_text += f"Тренд производства (production_trend): {'Положительный' if latest_metrics['growth_rate'] > 0.02 else 'Отрицательный' if latest_metrics['growth_rate'] < -0.02 else 'Стабильный'}\n"
            else:
                metrics_text += "Тренд производства (production_trend): N/A\n"
            
            if latest_metrics['consumption_growth_rate'] is not None:
                metrics_text += f"Тренд потребления (consumption_trend): {'Положительный' if latest_metrics['consumption_growth_rate'] > 0.02 else 'Отрицательный' if latest_metrics['consumption_growth_rate'] < -0.02 else 'Стабильный'}\n"
            else:
                metrics_text += "Тренд потребления (consumption_trend): N/A\n"
            
            metrics_text += f"Самообеспеченность: {latest_metrics['self_sufficiency']:.3f}\n"
            metrics_text += f"Зависимость от импорта: {latest_metrics['import_dependency']:.3f}\n"
            metrics_text += f"Доля производства: {latest_metrics['production_share']:.3f}\n"
            
            if latest_metrics['competitiveness_index'] is not None:
                metrics_text += f"Индекс конкурентоспособности: {latest_metrics['competitiveness_index']:.3f}\n"
            else:
                metrics_text += "Индекс конкурентоспособности: N/A\n"
    
    return metrics_text

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
st.title("📊  Единая аналитическая информационная система")

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
    
    # Информация о настройке API ключа
    st.markdown("---")
    st.markdown("### 🤖 Настройка ИИ")
    with st.expander("🔧 Настройка API ключа GigaChat"):
        st.markdown("""
        **Для получения рекомендаций от ИИ:**
        
        1. Получите API ключ на https://developers.sber.ru/portal/products/gigachat
        2. Создайте файл `.env` в корне проекта
        3. Добавьте: `GIGACHAT_API_KEY=ваш_ключ`
        4. Перезапустите приложение
        
        **Пример `.env`:**
        ```
        GIGACHAT_API_KEY=your_api_key_here
        ```
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
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Обзор", "📊 Анализ импорта РФ", "🏭 Анализ производства", "🎯 Рекомендации"])
    
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
    
    with tab3:
        st.header("🏭 Анализ производства и потребления товаров РФ")
        st.info("📊 **Информация**: Загрузите CSV файл с данными производства и потребления для анализа. Файл должен содержать колонки: category, year, manufacture, consumption, code. Данные импорта будут взяты из анализа импорта (вкладка 'Анализ импорта РФ').")
        st.divider()
        
        # Загрузка CSV файла
        uploaded_file = st.file_uploader(
            "📁 Загрузите CSV файл с данными производства и потребления",
            type=['csv'],
            help="Файл должен содержать колонки: category, year, manufacture, consumption, code"
        )
        
        if uploaded_file is not None:
            try:
                # Чтение CSV файла
                df_production = pd.read_csv(uploaded_file)
                
                # Проверка наличия необходимых колонок
                required_columns = ['category', 'year', 'manufacture', 'consumption', 'code']
                missing_columns = [col for col in required_columns if col not in df_production.columns]
                
                if missing_columns:
                    st.error(f"❌ В файле отсутствуют необходимые колонки: {missing_columns}")
                    st.info("📋 **Требуемые колонки**: category, year, manufacture, consumption, code")
                else:
                    # Отображение предварительного просмотра данных
                    st.subheader("📋 Предварительный просмотр данных")
                    st.dataframe(df_production.head(10), use_container_width=True)
                    
                    # Проверяем наличие данных импорта
                    if 'records' not in st.session_state:
                        st.warning("⚠️ **Внимание**: Для расчета метрик производства и потребления необходимо сначала выполнить анализ импорта (вкладка 'Анализ импорта РФ').")
                        st.info("💡 **Инструкция**: Перейдите на вкладку 'Анализ импорта РФ', введите код ТН ВЭД и нажмите 'Запустить анализ', затем вернитесь на эту вкладку.")
                    else:
                        # Расчет метрик
                        with st.spinner("🔄 Рассчитываем метрики производства и потребления..."):
                            try:
                                # Получаем данные импорта из session state
                                import_metrics_by_year = {}
                                for i, record in enumerate(st.session_state.records):
                                    year = st.session_state.years[i]
                                    import_metrics_by_year[year] = record
                                
                                # Получаем код ТН ВЭД из session state
                                tnved_code = st.session_state.get('tnved_code', None)
                                production_metrics = calculate_man_metrics(df_production, import_metrics_by_year, tnved_code)
                                summary_metrics = get_summary_metrics(production_metrics)
                                
                                # Сохранение в session state
                                st.session_state.production_metrics = production_metrics
                                st.session_state.summary_metrics = summary_metrics
                                st.session_state.production_df = df_production
                                st.session_state.import_metrics_by_year = import_metrics_by_year
                                
                                st.success("✅ Метрики успешно рассчитаны!")
                                
                            except Exception as e:
                                st.error(f"❌ Ошибка при расчете метрик: {str(e)}")
                                st.stop()
                    
                    # Отображение результатов
                    if 'production_metrics' in st.session_state:
                        st.subheader("📊 Анализ по категориям")
                        
                        # Выбор категории для детального анализа
                        categories = list(st.session_state.production_metrics.keys())
                        selected_category = st.selectbox(
                            "Выберите категорию для детального анализа:",
                            categories,
                            key="production_category_selector"
                        )
                        
                        if selected_category:
                            category_metrics = st.session_state.production_metrics[selected_category]
                            years = sorted(category_metrics.keys())
                            
                            # Основные метрики
                            st.subheader(f"📈 Ключевые показатели - {selected_category}")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                latest_year = max(years)
                                latest_metrics = category_metrics[latest_year]
                                st.metric(
                                    label="🏭 Самообеспеченность",
                                    value=f"{latest_metrics['self_sufficiency']:.2f}",
                                    delta="Полная" if latest_metrics['self_sufficiency'] >= 1.0 else "Частичная"
                                )
                            
                            with col2:
                                st.metric(
                                    label="📦 Доля производства",
                                    value=f"{latest_metrics['production_share']*100:.1f}%",
                                    delta="Высокая" if latest_metrics['production_share'] >= 0.7 else "Средняя" if latest_metrics['production_share'] >= 0.3 else "Низкая"
                                )
                            
                            with col3:
                                st.metric(
                                    label="📊 Зависимость от импорта",
                                    value=f"{latest_metrics['import_dependency']*100:.1f}%",
                                    delta="Критическая" if latest_metrics['import_dependency'] >= 0.3 else "Приемлемая"
                                )
                            
                            with col4:
                                growth_rate = latest_metrics['growth_rate']
                                if growth_rate is not None:
                                    st.metric(
                                        label="📈 Темп роста производства",
                                        value=f"{growth_rate*100:+.1f}%",
                                        delta="Рост" if growth_rate > 0 else "Снижение" if growth_rate < 0 else "Стабильно"
                                    )
                                else:
                                    st.metric(
                                        label="📈 Темп роста производства",
                                        value="N/A",
                                        delta="Нет данных"
                                    )
                            
                            # Графики
                            st.subheader("📊 Графики динамики")
                            
                            # Подготовка данных для графиков
                            production_data = [category_metrics[year]['manufacture'] for year in years]
                            consumption_data = [category_metrics[year]['consumption'] for year in years]
                            self_sufficiency_data = [category_metrics[year]['self_sufficiency'] for year in years]
                            import_dependency_data = [category_metrics[year]['import_dependency'] for year in years]
                            
                            # График производства и потребления
                            fig_prod_cons = create_production_chart(
                                years, production_data, consumption_data, 
                                "Производство и потребление", selected_category
                            )
                            st.plotly_chart(fig_prod_cons, use_container_width=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # График самообеспеченности
                                fig_self_suff = create_self_sufficiency_chart(
                                    years, self_sufficiency_data, 
                                    "Самообеспеченность", selected_category
                                )
                                st.plotly_chart(fig_self_suff, use_container_width=True)
                            
                            with col2:
                                # График зависимости от импорта
                                fig_import_dep = create_import_dependency_chart(
                                    years, import_dependency_data, 
                                    "Зависимость от импорта", selected_category
                                )
                                st.plotly_chart(fig_import_dep, use_container_width=True)
                            
                            # Радарная диаграмма
                            st.subheader("🎯 Радарная диаграмма метрик")
                            fig_radar = create_metrics_radar_chart(latest_metrics, selected_category)
                            st.plotly_chart(fig_radar, use_container_width=True)
                            
                            # Детальная таблица метрик
                            st.subheader("📋 Детальная таблица метрик")
                            
                            # Создаем DataFrame для отображения
                            metrics_table_data = []
                            for year in years:
                                year_metrics = category_metrics[year]
                                # Получаем данные импорта для данного года
                                import_val = 0
                                if 'import_metrics_by_year' in st.session_state and year in st.session_state.import_metrics_by_year:
                                    import_val = st.session_state.import_metrics_by_year[year].get('import_total', 0)
                                
                                metrics_table_data.append({
                                    'Год': year,
                                    'Производство': f"{year_metrics['manufacture']:,.0f}",
                                    'Потребление': f"{year_metrics['consumption']:,.0f}",
                                    'Импорт': f"{import_val:,.0f}",
                                    'Самообеспеченность': f"{year_metrics['self_sufficiency']:.3f}",
                                    'Доля производства': f"{year_metrics['production_share']:.3f}",
                                    'Зависимость от импорта': f"{year_metrics['import_dependency']:.3f}",
                                    'Темп роста производства': f"{year_metrics['growth_rate']:.3f}" if year_metrics['growth_rate'] is not None else "N/A",
                                    'Индекс конкурентоспособности': f"{year_metrics['competitiveness_index']:.3f}" if year_metrics['competitiveness_index'] is not None else "N/A"
                                })
                            
                            metrics_df = pd.DataFrame(metrics_table_data)
                            st.dataframe(metrics_df, use_container_width=True)
                        
                        # Сводная таблица по всем категориям
                        st.subheader("📊 Сводная таблица по всем категориям")
                        
                        summary_data = []
                        for category, metrics in st.session_state.summary_metrics.items():
                            summary_data.append({
                                'Категория': category,
                                'Последний год': metrics['latest_year'],
                                'Самообеспеченность': f"{metrics['self_sufficiency']:.3f}",
                                'Доля производства': f"{metrics['production_share']:.3f}",
                                'Зависимость от импорта': f"{metrics['import_dependency']:.3f}",
                                'Темп роста': f"{metrics['growth_rate']:.3f}" if metrics['growth_rate'] is not None else "N/A",
                                'Конкурентоспособность': f"{metrics['competitiveness_index']:.3f}" if metrics['competitiveness_index'] is not None else "N/A"
                            })
                        
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True)
                        
            except Exception as e:
                st.error(f"❌ Ошибка при чтении файла: {str(e)}")
                st.info("💡 **Подсказка**: Убедитесь, что файл имеет правильный формат CSV и содержит необходимые колонки.")
        else:
            st.info("📁 **Инструкция**: Загрузите CSV файл с данными производства и потребления для начала анализа.")
            
            # Пример структуры файла
            st.subheader("📋 Пример структуры CSV файла")
            example_data = {
                'category': ['Электроника', 'Электроника', 'Автомобили', 'Автомобили'],
                'year': [2021, 2022, 2021, 2022],
                'manufacture': [1000000, 1200000, 500000, 600000],
                'consumption': [1500000, 1800000, 800000, 900000],
                'code': ['8528', '8528', '8703', '8703']
            }
            example_df = pd.DataFrame(example_data)
            st.dataframe(example_df, use_container_width=True)
            
            st.markdown("""
            **Описание колонок:**
            - `category` - категория товара
            - `year` - год данных
            - `manufacture` - объем производства (в единицах измерения)
            - `consumption` - объем потребления (в единицах измерения)
            - `code` - код ТН ВЭД товара
            
            **Важно:** Данные импорта автоматически берутся из анализа импорта (вкладка 'Анализ импорта РФ').
            Убедитесь, что вы сначала выполнили анализ импорта для соответствующего кода ТН ВЭД.
            Код ТН ВЭД в CSV файле должен совпадать с кодом, используемым в анализе импорта.
            """)
    
    with tab4:
        st.header("🎯 Рекомендации по мерам ТТР")
        latest_year = st.session_state.years[-1]
        st.info(f"📊 **Информация**: В данной таблице представлены все рассчитанные метрики за {latest_year} год с их описаниями для анализа целесообразности применения мер таможенно-тарифного регулирования. Тренды рассчитаны за 3-летний период.")
        st.divider()
        
        # Кнопка для получения рекомендаций от LLM
        col1, col2 = st.columns([1, 1])
        
        with col1:
            get_recommendations = st.button("🤖 Получить рекомендации от ИИ", type="primary", use_container_width=True)
        
        with col2:
            show_metrics_table = st.checkbox("📋 Показать таблицу метрик", value=True, key="show_metrics_table")
        
        # Получение рекомендаций от LLM
        if get_recommendations:
            with st.spinner("🤖 Анализируем данные и формируем рекомендации..."):
                try:
                    # Форматируем метрики для LLM
                    metrics_text = format_metrics_for_llm()
                    
                    # Получаем рекомендации от LLM
                    llm_recommendations = get_llm_answer(metrics_text)
                    
                    # Сохраняем рекомендации в session state
                    st.session_state.llm_recommendations = llm_recommendations
                    
                    st.success("✅ Рекомендации успешно получены!")
                    
                except Exception as e:
                    st.error(f"❌ Ошибка при получении рекомендаций: {str(e)}")
                    st.info("💡 **Подсказка**: Убедитесь, что настроен API ключ для GigaChat в файле .env")
                    
                    # Показываем инструкцию по настройке API ключа
                    with st.expander("🔧 Инструкция по настройке API ключа GigaChat"):
                        st.markdown("""
                        **Для получения рекомендаций от ИИ необходимо настроить API ключ GigaChat:**
                        
                        1. **Получите API ключ:**
                           - Перейдите на https://developers.sber.ru/portal/products/gigachat
                           - Зарегистрируйтесь или войдите в аккаунт
                           - Создайте новый проект и получите API ключ
                        
                        2. **Создайте файл `.env`:**
                           - В корневой папке проекта создайте файл `.env`
                           - Добавьте в него строку: `GIGACHAT_API_KEY=ваш_api_ключ`
                        
                        3. **Пример файла `.env`:**
                           ```
                           GIGACHAT_API_KEY=your_actual_api_key_here
                           ```
                        
                        4. **Перезапустите приложение** после создания файла `.env`
                        
                        **Важно:** 
                        - Не добавляйте пробелы вокруг знака `=`
                        - Не коммитьте файл `.env` в git (он уже в .gitignore)
                        - Убедитесь, что API ключ активен и имеет права доступа к GigaChat API
                        """)
        
        # Отображение рекомендаций от LLM
        if 'llm_recommendations' in st.session_state:
            st.subheader("🤖 Рекомендации от ИИ")
            st.markdown("---")
            
            # Отображаем рекомендации в красивом формате
            st.markdown(st.session_state.llm_recommendations)
            
            st.markdown("---")
        
        # Отображение таблицы метрик (если включено)
        if show_metrics_table:
            # Создание сводной таблицы метрик
            def create_metrics_table():
                """Создает сводную таблицу всех метрик с описаниями"""
                
                # Получаем последние данные (самый новый год)
                latest_record = st.session_state.records[-1]
                trends = st.session_state.trends
                latest_year = st.session_state.years[-1]  # Последний год
            
                # Создаем таблицу метрик
                metrics_data = []
                
                # Основные метрики импорта (только за последний год)
                metrics_data.extend([
                    {
                        "Метрика": "import_total",
                        "Название": "Объём импорта товара из всех стран",
                        "Значение": f"{latest_record['import_total']:,.0f} $".replace(",", " "),
                        "Тренд": trends['trends']['import_total']['label'],
                        "Описание": f"Общий объём импорта товара в стоимостном выражении за {latest_year} год"
                    },
                    {
                        "Метрика": "import_friendly", 
                        "Название": "Импорт из дружественных стран",
                        "Значение": f"{latest_record['import_friendly']:,.0f} $".replace(",", " "),
                        "Тренд": "N/A",
                        "Описание": f"Объём импорта из стран, не включённых в перечень недружественных за {latest_year} год"
                    },
                    {
                        "Метрика": "import_unfriendly",
                        "Название": "Импорт из недружественных стран", 
                        "Значение": f"{latest_record['import_unfriendly']:,.0f} $".replace(",", " "),
                        "Тренд": "N/A",
                        "Описание": f"Объём импорта из стран по перечню распоряжения № 430-р за {latest_year} год"
                    },
                    {
                        "Метрика": "import_china",
                        "Название": "Импорт из Китая",
                        "Значение": f"{latest_record['import_china']:,.0f} $".replace(",", " "),
                        "Тренд": "N/A", 
                        "Описание": f"Объём импорта товара из Китайской Народной Республики за {latest_year} год"
                    }
                ])
            
                # Доли импорта (за последний год)
                metrics_data.extend([
                    {
                        "Метрика": "share_unfriendly",
                        "Название": "Доля импорта из недружественных стран",
                        "Значение": f"{latest_record['share_unfriendly']*100:.1f}%",
                        "Тренд": trends['trends']['share_unfriendly']['label'],
                        "Описание": f"Доля импорта из недружественных стран в общем объёме импорта за {latest_year} год. Критический порог: 30%"
                    },
                    {
                        "Метрика": "share_china", 
                        "Название": "Доля импорта из Китая",
                        "Значение": f"{latest_record['share_china']*100:.1f}%",
                        "Тренд": trends['trends']['share_china']['label'],
                        "Описание": f"Доля импорта из Китая в общем объёме импорта за {latest_year} год. Важно для анализа антидемпинговых мер"
                    }
                ])
            
                # Ценовые метрики (за последний год)
                price_metrics = []
                if not np.isnan(latest_record['price_china']):
                    price_metrics.append({
                        "Метрика": "price_china",
                        "Название": "Средняя контрактная цена из Китая",
                        "Значение": f"{latest_record['price_china']:.2f} $/ед.",
                        "Тренд": "N/A",
                        "Описание": f"Средняя контрактная цена импортируемых из Китая товаров за {latest_year} год (primaryValue/qty)"
                    })
                
                if not np.isnan(latest_record['price_others']):
                    price_metrics.append({
                        "Метрика": "price_others",
                        "Название": "Средняя контрактная цена из прочих стран",
                        "Значение": f"{latest_record['price_others']:.2f} $/ед.",
                        "Тренд": "N/A", 
                        "Описание": f"Средняя контрактная цена импортируемых из прочих стран товаров за {latest_year} год (primaryValue/qty)"
                    })
                
                if not np.isnan(latest_record['price_diff_ratio']):
                    dumping_status = "Демпинг" if latest_record['price_diff_ratio'] < 1.0 else "Норма"
                    price_metrics.append({
                        "Метрика": "price_diff_ratio",
                        "Название": "Отношение цен (Китай / прочие)",
                        "Значение": f"{latest_record['price_diff_ratio']:.2f}",
                        "Тренд": dumping_status,
                        "Описание": f"Отношение средней цены из Китая к средней цене из прочих стран за {latest_year} год. < 1.0 указывает на демпинг"
                    })
                
                metrics_data.extend(price_metrics)
            
                # Флаги для мер ТТР
                flags_data = []
                for flag_key, flag_value in trends['flags'].items():
                    flag_name = flag_key.replace("for_measure_", "Мера ").replace(":", ": ").replace("_", " ").title()
                    flags_data.append({
                        "Метрика": flag_key,
                        "Название": flag_name,
                        "Значение": str(flag_value),
                        "Тренд": "N/A",
                        "Описание": f"Флаг для определения применимости мер ТТР: {flag_key}"
                    })
                
                metrics_data.extend(flags_data)
            
                # Добавляем метрики производства и потребления, если они доступны
                if 'production_metrics' in st.session_state:
                    production_metrics = st.session_state.production_metrics
                    
                    # Добавляем заголовок для метрик производства
                    metrics_data.append({
                        "Метрика": "production_header",
                        "Название": "=== МЕТРИКИ ПРОИЗВОДСТВА И ПОТРЕБЛЕНИЯ ===",
                        "Значение": "---",
                        "Тренд": "---",
                        "Описание": "Метрики на основе данных производства и потребления товаров РФ"
                    })
                    
                    # Добавляем метрики по каждой категории
                    for category, category_metrics in production_metrics.items():
                        latest_year = max(category_metrics.keys())
                        latest_metrics = category_metrics[latest_year]
                        
                        # Основные метрики производства
                        production_metrics_list = [
                            {
                                "Метрика": f"production_self_sufficiency_{category}",
                                "Название": f"Самообеспеченность ({category})",
                                "Значение": f"{latest_metrics['self_sufficiency']:.3f}",
                                "Тренд": "N/A",
                                "Описание": f"Коэффициент самообеспеченности для категории {category} за {latest_year} год (производство/потребление)"
                            },
                            {
                                "Метрика": f"production_share_{category}",
                                "Название": f"Доля производства ({category})",
                                "Значение": f"{latest_metrics['production_share']:.3f}",
                                "Тренд": "N/A",
                                "Описание": f"Доля производства в общем объеме (производство + импорт) для категории {category} за {latest_year} год"
                            },
                            {
                                "Метрика": f"production_import_dependency_{category}",
                                "Название": f"Зависимость от импорта ({category})",
                                "Значение": f"{latest_metrics['import_dependency']:.3f}",
                                "Тренд": "N/A",
                                "Описание": f"Коэффициент зависимости от импорта для категории {category} за {latest_year} год (импорт/потребление)"
                            },
                            {
                                "Метрика": f"production_growth_rate_{category}",
                                "Название": f"Темп роста производства ({category})",
                                "Значение": f"{latest_metrics['growth_rate']:.3f}" if latest_metrics['growth_rate'] is not None else "N/A",
                                "Тренд": "N/A",
                                "Описание": f"Темп роста производства для категории {category} за {latest_year} год"
                            },
                            {
                                "Метрика": f"production_competitiveness_{category}",
                                "Название": f"Индекс конкурентоспособности ({category})",
                                "Значение": f"{latest_metrics['competitiveness_index']:.3f}" if latest_metrics['competitiveness_index'] is not None else "N/A",
                                "Тренд": "N/A",
                                "Описание": f"Индекс конкурентоспособности для категории {category} за {latest_year} год (производство/импорт)"
                            },
                            {
                                "Метрика": f"production_self_sufficiency_index_{category}",
                                "Название": f"Индекс самообеспеченности ({category})",
                                "Значение": f"{latest_metrics['self_sufficiency_index']:.3f}",
                                "Тренд": "N/A",
                                "Описание": f"Нормализованный индекс самообеспеченности для категории {category} за {latest_year} год (0-1)"
                            }
                        ]
                        
                        metrics_data.extend(production_metrics_list)
                
                return pd.DataFrame(metrics_data)
        
            # Создаем и отображаем таблицу
            metrics_df = create_metrics_table()
            
            # Отображаем таблицу с возможностью поиска и фильтрации
            st.subheader("📋 Сводная таблица метрик")
            
            # Добавляем фильтр по категориям
            filter_options = ["Все метрики", "Импорт", "Доли", "Цены", "Флаги ТТР"]
            if 'production_metrics' in st.session_state:
                filter_options.append("Производство и потребление")
            
            category_filter = st.selectbox(
                "Фильтр по категориям:",
                filter_options,
                key="metrics_filter"
            )
            
            # Фильтруем данные
            if category_filter == "Импорт":
                filtered_df = metrics_df[metrics_df['Метрика'].str.contains('import_')]
            elif category_filter == "Доли":
                filtered_df = metrics_df[metrics_df['Метрика'].str.contains('share_')]
            elif category_filter == "Цены":
                filtered_df = metrics_df[metrics_df['Метрика'].str.contains('price_')]
            elif category_filter == "Флаги ТТР":
                filtered_df = metrics_df[metrics_df['Метрика'].str.contains('for_measure_')]
            elif category_filter == "Производство и потребление":
                filtered_df = metrics_df[metrics_df['Метрика'].str.contains('production_')]
            else:
                filtered_df = metrics_df
            
            # Отображаем таблицу
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "Метрика": st.column_config.TextColumn("Код метрики", width="small"),
                    "Название": st.column_config.TextColumn("Название", width="medium"),
                    "Значение": st.column_config.TextColumn("Текущее значение", width="medium"),
                    "Тренд": st.column_config.TextColumn("Тренд/Статус", width="small"),
                    "Описание": st.column_config.TextColumn("Описание", width="large")
                }
            )
            
            # Дополнительная информация
            st.subheader("ℹ️ Пояснения к метрикам")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Ключевые пороговые значения:**
                - Доля НС > 30% → Мера ТТР №2
                - Доля Китая растёт + демпинг → Мера ТТР №3  
                - Отношение цен < 1.0 → Демпинг
                - Рост импорта + рост производства → Мера ТТР №5
                """)
            
            with col2:
                st.markdown("""
                **Тренды:**
                - **Положительный** - рост показателя
                - **Отрицательный** - снижение показателя  
                - **Стабильный** - незначительные изменения
                - **N/A** - тренд не рассчитывается
                """)
            
            # Информация о годах анализа
            st.info(f"📅 **Метрики показаны за**: {st.session_state.years[-1]} год (последний доступный)")
            st.info(f"📈 **Тренды рассчитаны за период**: {st.session_state.years[0]} - {st.session_state.years[2]} годы")
            st.info(f"🔢 **Код ТН ВЭД**: {st.session_state.tnved_code}")

# Футер
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("📊 **Анализ импорта РФ** | Создано с помощью Streamlit")
    st.caption("Данные предоставлены UN Comtrade API")
