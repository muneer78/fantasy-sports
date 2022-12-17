import pandas as pd

df = pd.read_csv("Fangraphs Leaderboard.csv", index_col=["playerid"]) #10 IP Pitchers
df = pd.read_csv("Fangraphs Leaderboard (1).csv", index_col=["playerid"]) #30 IP Pitchers
df = pd.read_csv("Fangraphs Leaderboard (5).csv", index_col=["playerid"]) #Pitchers Last 14 Days
df = pd.read_csv("Fangraphs Leaderboard 6).csv", index_col=["playerid"]) #Pitchers Last 30 Days

df.columns = df.columns.str.replace('[+,-,%,]', '')
df.rename(columns={'K-BB':'KMinusBB','K/BB':'KToBB', 'HR/9':'HRPer9', 'xFIP-':'XFIPMinus'}, inplace=True)
df.fillna(0)

df['KMinusBB'] = df['KMinusBB'] = df['KMinusBB'].str.rstrip('%').astype('float')
df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')
df['CSW'] = df['CSW'] = df['CSW'].str.rstrip('%').astype('float')

filters1 = df[(df['xERA'] < 3) & (df['Barrel'] < 7) & (df['KMinusBB'] > 20) & (df['Starting'] > 5) & (df['GS'] > 1)] 
filters2 = df[(df['xERA'] < 3) & (df['Barrel'] < 7) & (df['KMinusBB'] > 30) & (df['Relieving'] > 1)] 

finalSP=(filters1.drop(['Relieving'],axis=1))
finalRP=(filters2.drop(['Starting'],axis=1))

finalSP.to_excel("pitchingSP.xlsx", sheet_name='StartersSeason')
finalRP.to_excel("pitchingRP.xlsx", sheet_name='RelieversSeason')