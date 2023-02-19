import pandas as pd
from functools import partial, reduce

dffg = pd.read_csv("fg2.csv")
dfstuff = pd.read_csv("stuffplus.csv")
dfadp= pd.read_csv("adp.csv")

dffg = dffg.replace(r'[^\w\s]|_\*', '', regex=True)
dfstuff = dfstuff.replace(r'[^\w\s]|_\*', '', regex=True)
dfadp= dfadp.replace(r'[^\w\s]|_\*', '', regex=True)

#func = lambda x: ''.join([i[:3] for i in x.strip().split(' ')])
#dffg['Key'] = dffg.Name.apply(func)
#dfstuff['Key'] = dfstuff.player_name.apply(func)
#dfadp['Key'] = dfadp.Player.apply(func)
#dfadp['Key'] = dfadp['Key'].astype(str)

#dffg.columns = dffg.columns.str.strip()
#dfstuff.columns = dfstuff.columns.str.strip()
#dfadp.columns = dfadp.columns.str.strip()

#dfs = [dffg, dfadp, dfstuff]
#merge = partial(pd.merge, on=['Key'], how='outer')
#reduce(merge, dfs)

df1 = dfadp.merge(dffg, how="left", on=["Key"])\
    #.merge(dfstuff, how="left", on=["Key"])

df1=dfs.drop(['MLBAMID','playerid','player_name','Key'], axis=1)
df1.to_csv('ranks.csv')