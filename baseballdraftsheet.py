import pandas as pd
from functools import partial, reduce

dffg = pd.read_csv("fg2.csv")
dfstuff = pd.read_csv("stuffplus.csv")
dfadp= pd.read_csv("adp.csv")

dffg = dffg.replace(r'[^\w\s]|_\*', '', regex=True)
dfstuff = dfstuff.replace(r'[^\w\s]|_\*', '', regex=True)
dfadp= dfadp.replace(r'[^\w\s]|_\*', '', regex=True)

dfadp = dfadp.astype(str)

func = lambda x: ''.join([i[:3] for i in x.strip().split(' ')])
dffg['Key'] = dffg.Name.apply(func)
dfstuff['Key'] = dfstuff.player_name.apply(func)
dfadp['Key'] = dfadp.Player.apply(func)func = lambda x: ''.join([i[:3] for i in x.strip().split(' ')])
dffg['Key'] = dffg.Name.apply(func)
dfstuff['Key'] = dfstuff.player_name.apply(func)
dfadp['Key'] = dfadp.Player.apply(func)

dffg.columns = dffg.columns.str.strip()
dfstuff.columns = dfstuff.columns.str.strip()
dfadp.columns = dfadp.columns.str.strip()

df1 = dfadp.merge(dffg, how="left", on=["Key"]).merge(dfstuff, how="left", on=["Key"])

df1 = df1.drop(['MLBAMID','playerid','player_name','Key','ESPN','CBS','RTS','NFBC','FT'], axis=1)

df1 = df1.fillna('')

df1.to_csv('output.csv')