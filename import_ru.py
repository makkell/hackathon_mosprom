import pandas as pd
from datetime import datetime
import comtradeapicall

UNFRIENDLY = {
    'Australia', 'Albania', 'Andorra', 'United Kingdom', 'Iceland', 'Canada',
    'New Zealand', 'Norway', 'Rep. of Korea', 'North Macedonia', 'Singapore',
    'USA', 'Ukraine', 'Montenegro', 'Switzerland', 'Japan',
    'Austria', 'Belgium', 'Bulgaria', 'Hungary', 'Germany', 'Greece', 'Denmark',
    'Ireland', 'Spain', 'Italy', 'Cyprus', 'Latvia', 'Lithuania', 'Luxembourg',
    'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia',
    'Slovenia', 'Finland', 'France', 'Croatia', 'Czechia', 'Sweden', 'Estonia'
}
CHINA = 'China'

def download_by_tnved(cmd_code: str):
    """Загружает данные по указанному коду ТН ВЭД за последние 3 года"""
    now = datetime.now()
    years = [now.year - 1, now.year - 2, now.year - 3]

    df = pd.DataFrame()
    for year in years:
        data = comtradeapicall.previewFinalData(
            typeCode='C', freqCode='A', clCode='HS', period=year,
            reporterCode=None, cmdCode=str(cmd_code), flowCode='X',
            partnerCode='643', format_output='JSON', includeDesc=True,
            partner2Code=None, customsCode=None, motCode=None, maxRecords=50000
        )
        df = pd.concat([df, data], ignore_index=True)
    return df

def mark_friendly(df: pd.DataFrame):
    """Добавляет колонку isFriendly: 1 — дружественная, 0 — недружественная"""
    if 'reporterDesc' in df.columns:
        df['isFriendly'] = df['reporterDesc'].apply(lambda x: 0 if x in UNFRIENDLY else 1)
    return df
