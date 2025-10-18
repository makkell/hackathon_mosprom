import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
CHINA = 'China'

def _norm_year(y):
    # год может прийти как int, [2024], np.array([2024]) — приведём к int
    if isinstance(y, (list, tuple, np.ndarray)) and len(y) > 0:
        return int(y[0])
    return int(y)

def _trend(values, years, eps=0.02):
    """Возвращает (delta_abs, delta_pct, cagr, label) для ряда за 3 года."""
    y = np.asarray(values, dtype=float)
    x = np.asarray(years, dtype=float)
    first, last = y[0], y[-1]
    delta_abs = last - first
    delta_pct = (delta_abs / first) if first != 0 else np.nan
    # CAGR на (len-1) интервалов
    n = len(y) - 1
    cagr = (last/first)**(1/n) - 1 if (first > 0 and last > 0) else np.nan
    # простой ярлык
    if np.isnan(delta_pct):
        label = "Стабильный"
    elif delta_pct > eps:
        label = "Положительный"
    elif delta_pct < -eps:
        label = "Отрицательный"
    else:
        label = "Стабильный"
    return float(delta_abs), float(delta_pct) if not np.isnan(delta_pct) else np.nan, \
           float(cagr) if not np.isnan(cagr) else np.nan, label

def summarize_trends(records, plot=False):
    """
    records: список из 3 dict, каждый как в примере пользователя.
    Возвращает:
      - yearly (отсортированный список по году)
      - trends (словарь по метрикам)
      - flags (булевы/текстовые флаги под меры)
    """
    # 1) нормализуем и сортируем по году
    items = []
    for r in records:
        yr = _norm_year(r.get("year"))
        items.append((yr, r))
    items.sort(key=lambda t: t[0])
    years = [t[0] for t in items]
    data  = [t[1] for t in items]
    # 2) соберём нужные ряды
    series = {
        "import_total":     [d["import_total"]     for d in data],
        "share_unfriendly": [d["share_unfriendly"] for d in data],
        "share_china":      [d["share_china"]      for d in data],
        "price_diff_ratio": [d.get("price_diff_ratio", np.nan) for d in data],
    }

    # 3) посчитаем тренды (только для трёх метрик)
    trends = {}
    for key, title, is_percent in [
        ("import_total", "Импорт, всего", False),
        ("share_unfriendly", "Доля НС", True),
        ("share_china", "Доля Китая", True),
    ]:
        da, dp, cagr, label = _trend(series[key], years)
        trends[key] = {
            "title": title,
            "first": series[key][0],
            "last":  series[key][-1],
            "delta_abs": da,
            "delta_pct": dp,
            "cagr": cagr,
            "label": label,
        }
        if plot:
            vals = np.array(series[key], dtype=float)
            years_int = [int(y) for y in years]
            
            # Создаем Plotly график
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years_int,
                y=vals,
                mode='lines+markers',
                name=title,
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10, color='#1f77b4'),
                hovertemplate=f'{title}<br>Год: %{{x}}<br>Значение: %{{y}}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{title} - тренд: {label}",
                xaxis_title="Год",
                yaxis_title=title,
                font=dict(size=12),
                height=400,
                hovermode='x unified'
            )
            
            # Добавляем аннотации с значениями
            for x, yv in zip(years_int, vals):
                if np.isnan(yv): 
                    continue
                txt = f"{yv*100:.1f}%" if is_percent else f"{yv:,.0f}".replace(",", " ")
                fig.add_annotation(
                    x=x,
                    y=yv,
                    text=txt,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#1f77b4",
                    ax=0,
                    ay=-30,
                    font=dict(size=10, color="#1f77b4")
                )
            
            fig.show()


    # 4) флаги для мер
    dumping_flag = bool(np.isfinite(series["price_diff_ratio"][-1]) and series["price_diff_ratio"][-1] < 1.0)
    flags = {
        "for_measure_1_2:share_unfriendly_trend": trends["share_unfriendly"]["label"],
        "for_measure_3:share_china_trend": trends["share_china"]["label"],
        "for_measure_3:dumping_flag(price_ratio<1)": dumping_flag,
        "for_measure_5:import_total_trend": trends["import_total"]["label"],
    }

    return {"years": years, "yearly": data, "trends": trends, "flags": flags}

def pie_friendly_unfriendly_with_china(
    df_year: pd.DataFrame,
    *,
    value_col: str = "primaryValue",
    friendly_col: str = "isFriendly",
    partner_iso_col: str = "partnerISO",
    partner_desc_col: str = "partnerDesc",
    china_iso: str = "CHN",
    china_name_token: str = "China",
    title: str | None = None,
):
    d = df_year.copy()

    # приведение типов и защита от NaN
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    if friendly_col not in d.columns:
        raise KeyError(f"Не найдена колонка {friendly_col}")
    # маска Китая — по ISO; если его нет, fallback по названию
    mask_china = df_year['reporterDesc'].str.contains(CHINA)

    mask_friend = d[friendly_col].isin([1, True, "1", "true", "True"])

    # суммы по категориям
    val_china = float(d.loc[mask_china, value_col].sum())
    val_friend_other = float(d.loc[mask_friend & ~mask_china, value_col].sum())
    val_unfriendly = float(d.loc[~mask_friend, value_col].sum())
    total = val_china + val_friend_other + val_unfriendly

    if total <= 0:
        print("Нет данных для визуализации (total == 0). Проверь фильтры по году/потоку.")
        return pd.DataFrame(columns=["segment", "value", "share"])

    # доли
    shares = np.array([val_china, val_friend_other, val_unfriendly]) / total
    labels = ["Китай", "Другие дружественные", "Недружественные"]

    # табличка-резюме (удобно дальше использовать)
    summary = pd.DataFrame({
        "segment": labels,
        "value": [val_china, val_friend_other, val_unfriendly],
        "share": shares
    })

    # заголовок
    if title is None:
        if "refYear" in d.columns and d["refYear"].nunique() == 1:
            year_val = int(d["refYear"].dropna().iloc[0])
            title = f"Структура импорта по стоимости, {year_val}"
        else:
            title = "Структура импорта по стоимости за последние 3 года"

    # круговая диаграмма Plotly
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    fig = go.Figure(data=[go.Pie(
        labels=summary["segment"],
        values=summary["value"],
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title=title,
        font=dict(size=14),
        showlegend=True,
        height=500
    )
    
    fig.show()