import pandas as pd

def percent_to_float(s):
  float(stringPercent[:-1]) / 100

df = pd.read_csv("fangraphs.csv", index_col=["playerid"])

df.columns = df.columns.str.replace('[+,-,%,]', '')
df.rename(columns={'K-BB':'KMinusBB','K/BB':'KToBB', 'HR/9':'HRPer9', 'xFIP-':'XFIPMinus'}, inplace=True)
df.fillna(0)

df['KBB'] = df['KMinusBB'] = df['KMinusBB'].str.rstrip('%').astype('float')
df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')
df['CSW'] = df['CSW'] = df['CSW'].str.rstrip('%').astype('float')

filters1 = df[(df['xERA'] < 3) & (df['Barrel'] < 5) & (df['CSW'] > 20) & (df['KMinusBB'] > 20) & (df['Starting'] > 5)] 
filters2 = df[(df['xERA'] < 3) & (df['Barrel'] < 5) & (df['CSW'] > 20) & (df['KMinusBB'] > 30) & (df['Relieving'] > 1)] 


print(filters1.head())
print(filters1.shape)

print(filters2.head())
print(filters2.shape)

filters1.to_excel("pitchingSP.xlsx", sheet_name='StartersSeason')
filters2.to_excel("pitchingRP.xlsx", sheet_name='RelieversSeason')