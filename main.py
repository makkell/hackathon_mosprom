from import_ru import download_by_tnved, mark_friendly
from datetime import datetime
from calc_import_metrics import calc_import_metrics
from draw_image import summarize_trends

df = download_by_tnved('8528')
df = mark_friendly(df)
col = ['refYear', 'reporterDesc', 'isFriendly', 'primaryValue', 'qty', 'qtyUnitCode', 'netWgt','partnerDesc']
df_proc = df[col].copy()
now = datetime.now()
years = [now.year - 1, now.year - 2, now.year - 3]

df_proc_year_1 = df_proc[df_proc['refYear'] == years[0]].sort_values(by='primaryValue', ascending=False).copy()
df_proc_year_2 = df_proc[df_proc['refYear'] == years[1]].sort_values(by='primaryValue', ascending=False).copy()
df_proc_year_3 = df_proc[df_proc['refYear'] == years[2]].sort_values(by='primaryValue', ascending=False).copy()


records = []

records.append(calc_import_metrics(df_proc_year_1))
records.append(calc_import_metrics(df_proc_year_2))
records.append(calc_import_metrics(df_proc_year_3))
print(records)

res = summarize_trends(records, plot=True)  
print(res["trends"])
print(res["flags"])