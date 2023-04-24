import pandas as pd
from datetime import date, datetime, timedelta
import os
import csv

# define dictionary
comp_dict = {'FanGraphs Leaderboard.csv': 'fgl_pitchers_10_ip.csv',
            'FanGraphs Leaderboard (1).csv': 'fgl_pitchers_30_ip.csv',
            'FanGraphs Leaderboard (2).csv': 'fgl_hitters_40_pa.csv',
            'FanGraphs Leaderboard (3).csv': 'fgl_hitters_last_14.csv',
            'FanGraphs Leaderboard (4).csv': 'fgl_hitters_last_7.csv',
            'FanGraphs Leaderboard (5).csv': 'fgl_pitchers_last_14.csv',
            'FanGraphs Leaderboard (6).csv': 'fgl_pitchers_last_30.csv',
             }

for newname, oldname in comp_dict.items():
    os.replace(newname, oldname)

excluded = pd.read_csv('excluded.csv')

today = date.today()
today = datetime.strptime('2023-10-31', '%Y-%m-%d').date() # pinning to last day of baseball season

def hitters_preprocessing(filepath):
    df = pd.read_csv(filepath, index_col=["playerid"])
    # df = pd.read_csv(filepath, index_col=["Name"])

    df.columns = df.columns.str.replace('[+,-,%,]', '', regex=True)
    df.rename(columns={'K%-': 'K', 'BB%-': 'BB'}, inplace=True)
    df.fillna(0)
    df.reset_index(inplace=True)
    df = df[~df['playerid'].isin(excluded['playerid'])]
    df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')

    filters = df[(df['wRC'] > 135) & (df['OPS'] > .8) & (df['K'] < 95) & (df['BB'] > 100) & (df['Off'] > 1) & (
                df['Barrel'] > 10)].sort_values(by='Off', ascending=False)
    return filters

def pitchers_preprocessing(filepath):
    df = pd.read_csv(filepath, index_col=["playerid"])

    df.columns = df.columns.str.replace('[+,-,%,]', '', regex=True)
    df.rename(columns={'K/BB': 'KToBB', 'HR/9': 'HRPer9', 'xFIP-': 'XFIPMinus'}, inplace=True)
    df.fillna(0)
    df.reset_index(inplace=True)
    df = df[~df['playerid'].isin(excluded['playerid'])]

    df['Barrel'] = df['Barrel'] = df['Barrel'].str.rstrip('%').astype('float')
    df['CSW'] = df['CSW'] = df['CSW'].str.rstrip('%').astype('float')

    filters1 = df[(df['Barrel'] < 7) & (df['Starting'] > 5) & (df['GS'] > 1) & (df['Pitching'] > 99)].sort_values(by='Starting', ascending=False)
    filters2 = df[(df['Barrel'] < 7) & (df['Relieving'] > 1) & (df['Pitching'] > 99)].sort_values(by='Relieving', ascending=False)
    return filters1
    return filters2

# Preprocess and export the dataframes to Excel workbook sheets
hitdaywindow = [7, 14]
pawindow = [40]
pitchdaywindow = [14, 30]
ipwindow = [10, 30]

df_list = []

with open('weeklyadds.csv', 'w+') as f:
    for w in hitdaywindow:
        f.write(f'Hitters Last {w} Days\n\n')
        df = hitters_preprocessing(f'fgl_hitters_last_{w}.csv')
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write('\n')

    for w in pawindow:
        f.write(f'Hitters {w} PA\n\n')
        df = hitters_preprocessing(f'fgl_hitters_{w}_pa.csv')
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write('\n')

    for w in ipwindow:
        f.write(f'Pitchers Last {w} Innings\n\n')
        df = pitchers_preprocessing(f'fgl_pitchers_{w}_ip.csv')
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write('\n')

    for w in pitchdaywindow:
        f.write(f'Pitchers Last {w} Days\n\n')
        df = pitchers_preprocessing(f'fgl_pitchers_last_{w}.csv')
        df_list.append(df)
        df.to_csv(f, index=False)
        f.write('\n')