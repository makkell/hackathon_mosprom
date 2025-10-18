import pandas as pd
import numpy as np

def calculate_man_metrics(df_production, import_metrics_by_year, tnved_code=None):
    """
    Рассчитывает метрики производства и потребления товаров РФ
    
    Args:
        df_production (pd.DataFrame): DataFrame с колонками ['category', 'year', 'manufacture', 'consumption', 'code']
        import_metrics_by_year (dict): Словарь с метриками импорта по годам из calc_import_metrics
        tnved_code (str): Код ТН ВЭД для фильтрации данных импорта
        
    Returns:
        dict: Словарь с метриками по категориям и годам
    """
    if df_production.empty:
        return {}
    
    # Проверяем наличие необходимых колонок
    required_columns = ['category', 'year', 'manufacture', 'consumption']
    missing_columns = [col for col in required_columns if col not in df_production.columns]
    if missing_columns:
        raise ValueError(f"Отсутствуют необходимые колонки: {missing_columns}")
    
    metrics_dict = {}
    df_sorted = df_production.sort_values(['category', 'year']).copy()
    
    for category in df_production['category'].unique():
        category_data = df_sorted[df_sorted['category'] == category].copy()
        category_metrics = {}
        
        # Сортировка по году для категорий
        category_data = category_data.sort_values('year')
        
        for idx, row in category_data.iterrows():
            year = row['year']
            manufacture = float(row['manufacture']) if pd.notna(row['manufacture']) else 0
            consumption = float(row['consumption']) if pd.notna(row['consumption']) else 0
            
            # Получаем код ТН ВЭД для данной категории
            category_tnved_code = None
            if 'code' in row and pd.notna(row['code']):
                category_tnved_code = str(row['code'])
            elif tnved_code:
                category_tnved_code = str(tnved_code)
            
            # Получаем данные импорта для данного года и кода ТН ВЭД
            import_val = 0
            if year in import_metrics_by_year and category_tnved_code:
                # Используем данные импорта для конкретного кода ТН ВЭД
                import_val = import_metrics_by_year[year].get('import_total', 0)
            
            # Основные метрики
            self_sufficiency = manufacture / consumption if consumption > 0 else 0
            balance = manufacture - consumption
            
            # Зависимость от импорта = доля импорта в покрытии нехватки производства
            # Если производство покрывает потребление полностью, то зависимость = 0
            # Если производство не покрывает потребление, то импорт покрывает нехватку
            production_deficit = max(0, consumption - manufacture)  # Нехватка производства
            if production_deficit > 0:
                import_dependency = min(import_val / production_deficit, 1.0)  # Ограничиваем до 100%
            else:
                import_dependency = 0  # Если производство покрывает потребление, зависимость = 0
            
            # Доля производства в общем предложении (производство + импорт)
            total_supply = manufacture + import_val
            production_share = manufacture / total_supply if total_supply > 0 else 0
            
            # Дополнительные метрики
            consumption_coverage = min(manufacture / consumption, 1.0) if consumption > 0 else 0
            import_penetration = import_val / (manufacture + import_val) if (manufacture + import_val) > 0 else 0
            production_efficiency = manufacture / (manufacture + import_val) if (manufacture + import_val) > 0 else 0
            
            # Темп роста производства
            growth_rate = None
            prev_year_data = category_data[category_data['year'] == year - 1]
            if not prev_year_data.empty:
                prev_manufacture = float(prev_year_data['manufacture'].iloc[0]) if pd.notna(prev_year_data['manufacture'].iloc[0]) else 0
                if prev_manufacture > 0:
                    growth_rate = (manufacture - prev_manufacture) / prev_manufacture
            
            # Темп роста потребления
            consumption_growth_rate = None
            if not prev_year_data.empty:
                prev_consumption = float(prev_year_data['consumption'].iloc[0]) if pd.notna(prev_year_data['consumption'].iloc[0]) else 0
                if prev_consumption > 0:
                    consumption_growth_rate = (consumption - prev_consumption) / prev_consumption
            
            # Темп роста импорта
            import_growth_rate = None
            if not prev_year_data.empty:
                # Получаем данные импорта для предыдущего года
                prev_year = year - 1
                prev_import = 0
                if prev_year in import_metrics_by_year:
                    prev_import = import_metrics_by_year[prev_year].get('import_total', 0)
                if prev_import > 0:
                    import_growth_rate = (import_val - prev_import) / prev_import
            
            # Индекс конкурентоспособности (производство vs импорт)
            competitiveness_index = manufacture / import_val if import_val > 0 else float('inf')
            
            # Индекс самообеспеченности (0-1, где 1 = полная самообеспеченность)
            self_sufficiency_index = min(manufacture / consumption, 1.0) if consumption > 0 else 0
            
            category_metrics[year] = {
                # Основные метрики
                'self_sufficiency': round(self_sufficiency, 4),
                'balance': round(balance, 2),
                'growth_rate': round(growth_rate, 4) if growth_rate is not None else None,
                'import_dependency': round(import_dependency, 4),
                'production_share': round(production_share, 4),
                
                # Дополнительные метрики
                'consumption_coverage': round(consumption_coverage, 4),
                'import_penetration': round(import_penetration, 4),
                'production_efficiency': round(production_efficiency, 4),
                'consumption_growth_rate': round(consumption_growth_rate, 4) if consumption_growth_rate is not None else None,
                'import_growth_rate': round(import_growth_rate, 4) if import_growth_rate is not None else None,
                'competitiveness_index': round(competitiveness_index, 4) if competitiveness_index != float('inf') else None,
                'self_sufficiency_index': round(self_sufficiency_index, 4),
                
                # Исходные данные
                'manufacture': manufacture,
                'consumption': consumption
            }
        
        metrics_dict[category] = category_metrics
    
    return metrics_dict

def get_summary_metrics(metrics_dict):
    """
    Получает сводные метрики по всем категориям
    
    Args:
        metrics_dict (dict): Результат calculate_man_metrics
        
    Returns:
        dict: Сводные метрики
    """
    if not metrics_dict:
        return {}
    
    summary = {}
    
    for category, category_metrics in metrics_dict.items():
        # Получаем последний год
        latest_year = max(category_metrics.keys())
        latest_metrics = category_metrics[latest_year]
        
        summary[category] = {
            'latest_year': latest_year,
            'self_sufficiency': latest_metrics['self_sufficiency'],
            'production_share': latest_metrics['production_share'],
            'import_dependency': latest_metrics['import_dependency'],
            'growth_rate': latest_metrics['growth_rate'],
            'competitiveness_index': latest_metrics['competitiveness_index'],
            'self_sufficiency_index': latest_metrics['self_sufficiency_index']
        }
    
    return summary