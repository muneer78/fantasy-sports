import pandas as pd

df = pd.read_csv("fangraphs.csv", index_col=["playerid"])

df.columns = df.columns.str.replace('[+,-,%,]', '')
df.rename(columns={'K-BB':'KMinusBB','K/BB':'KToBB', 'HR/9':'HRPer9', 'xFIP-':'XFIPMinus'}, inplace=True)
df.fillna(0)

df['KMinusBB'] = df['KMinusBB'] = df['KMinusBB'].str.rstrip('%').astype('float')
df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')
df['CSW'] = df['CSW'] = df['CSW'].str.rstrip('%').astype('float')

filters1 = df[(df['xERA'] < 3) & (df['Barrel'] < 7) & (df['KMinusBB'] > 20) & (df['Starting'] > 5)] 
filters2 = df[(df['xERA'] < 3) & (df['Barrel'] < 7) & (df['KMinusBB'] > 30) & (df['Relieving'] > 1)] 

finalSP=(filters1.drop(['Relieving'],axis=1))
finalRP=(filters2.drop(['Starting'],axis=1))

finalSP.to_excel("pitchingSP.xlsx", sheet_name='StartersSeason')
finalRP.to_excel("pitchingRP.xlsx", sheet_name='RelieversSeason')