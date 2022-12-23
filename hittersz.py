import pandas as pd
from scipy import stats

df = pd.read_csv("hitters.csv", index_col=["playerid"]) #Preseason Hitters

df['Barrel%'] = df['Barrel%'] = df['Barrel%'].str.rstrip('%').astype('float')

df = df.select_dtypes(include='number').apply(stats.zscore)

df['Total Z-Score']= df.sum(axis = 1)

df.iloc[:, 0:22] 

rounded_df = df.round(decimals=2).sort_values(by='Total Z-Score', ascending=False)

rounded_df.to_excel("Hitters.xlsx", sheet_name='Hitters')