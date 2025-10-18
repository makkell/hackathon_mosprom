import numpy as np
import pandas as pd

CHINA = 'China'

def calc_import_metrics(
    df_year: pd.DataFrame,
    *,
    value_col: str = "primaryValue",
    qty_col: str = "qty",
    friendly_col: str = "isFriendly",
    country_col: str = "partnerDesc",
    china_mask_col: str = "partnerISO",  # 'partnerISO' или 'reporterDesc'
    china_value: str = "CHN",            # 'CHN' или 'China'
):
    d = df_year.copy()

    # Приводим типы
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    d[qty_col] = pd.to_numeric(d[qty_col], errors="coerce")

    # Маска Китая
    mask_china = df_year['reporterDesc'].str.contains(CHINA)

    # Маска дружественных
    mask_friend = d[friendly_col] == 1

    # БАЗОВЫЕ МЕТРИКИ
    total_import = d[value_col].sum()
    import_from_is_friend = d.loc[mask_friend, value_col].sum()
    import_from_is_not_friend = d.loc[~mask_friend, value_col].sum()
    import_from_china = d.loc[mask_china, value_col].sum()

    share_unfriendly = float(import_from_is_not_friend / total_import) if total_import else 0.0
    share_china = float(import_from_china / total_import) if total_import else 0.0

    # КОНТРАКТНАЯ ЦЕНА: primaryValue / qty (если qty > 0 и qty != -1)
    valid_qty_mask = d[qty_col].notna() & (d[qty_col] > 0) & (d[qty_col] != -1)

    # Страны, где qty == -1
    countries_no_qty = (
        d.loc[d[qty_col] == -1, country_col]
        .astype(str)
        .dropna()
        .unique()
        .tolist()
        if qty_col in d.columns
        else []
    )

    # Цена для Китая
    val_china = d.loc[mask_china & valid_qty_mask, value_col].sum()
    qty_china = d.loc[mask_china & valid_qty_mask, qty_col].sum()
    price_china = float(val_china / qty_china) if qty_china and qty_china > 0 else float("nan")

    # Цена для прочих
    val_others = d.loc[~mask_china & valid_qty_mask, value_col].sum()
    qty_others = d.loc[~mask_china & valid_qty_mask, qty_col].sum()
    price_others = float(val_others / qty_others) if qty_others and qty_others > 0 else float("nan")

    price_diff_ratio = (
        float(price_china / price_others) if (price_china and price_others) else float("nan")
    )

    # # Вывод результатов
    # print(f"Всего импорт: {total_import}")
    # print(f"ДС импорт: {import_from_is_friend}")
    # print(f"НС импорт: {import_from_is_not_friend}")
    # print(f"Китай импорт: {import_from_china}")
    # print(f"Доля импорта из НС: {share_unfriendly}")
    # print(f"Доля импорта из Китая: {share_china}")

    # Контрактные цены
    if not np.isnan(price_china):
        print(f"Контрактная цена Китая (primaryValue/qty): {price_china}")
    else:
        print("Контрактная цена Китая не рассчитана (нет валидного qty для Китая).")

    if not np.isnan(price_others):
        print(f"Контрактная цена прочих стран (primaryValue/qty): {price_others}")
    else:
        print("Контрактная цена прочих стран не рассчитана (нет валидного qty у прочих стран).")

    if not np.isnan(price_diff_ratio):
        print(f"Отношение цен (Китай / прочие): {price_diff_ratio}")
    else:
        print("Отношение цен не рассчитано.")

    # Уведомление о странах без qty
    if countries_no_qty:
        preview = countries_no_qty[:10]
        more = len(countries_no_qty) - len(preview)
        msg = f"Страны с qty = -1 (исключены из расчёта цены): {', '.join(preview)}"
        if more > 0:
            msg += f" и ещё {more}…"
        print(msg)

    return {
        "import_total": float(total_import),
        "import_friendly": float(import_from_is_friend),
        "import_unfriendly": float(import_from_is_not_friend),
        "import_china": float(import_from_china),
        "share_unfriendly": share_unfriendly,
        "share_china": share_china,
        "price_china": price_china,
        "price_others": price_others,
        "price_diff_ratio": price_diff_ratio,
        "countries_no_qty": countries_no_qty,
        "year" : df_year['refYear'].unique()
    }
