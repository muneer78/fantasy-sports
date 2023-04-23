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

for w in hitdaywindow:
    df = hitters_preprocessing(f'fgl_hitters_last_{w}.csv')
    df.to_csv(f'Hitters Last {w} Days.csv', index=False)

for w in pawindow:
    df = hitters_preprocessing(f'fgl_hitters_{w}_pa.csv')
    df.to_csv(f'Hitters {w} PA.csv', index=False)

for w in ipwindow:
    df = pitchers_preprocessing(f'fgl_pitchers_{w}_ip.csv')
    df.to_csv(f'Pitchers Last {w} Innings.csv', index=False)

for w in pitchdaywindow:
    df = pitchers_preprocessing(f'fgl_pitchers_last_{w}.csv')
    df.to_csv(f'Pitchers Last {w} Days.csv', index=False)

# # Create a new CSV file or append to an existing one
# with open('weeklypickups.csv', mode='w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(['Dataframe Name', 'Data'])
#
# for w in hitdaywindow:
#     df = hitters_preprocessing(f'fgl_hitters_last_{w}.csv')
#     with open('output.csv', mode='a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([f'fgl_hitters_last_{w}', df.to_string(index=False)])
#
# for w in pawindow:
#     df = hitters_preprocessing(f'fgl_hitters_{w}_pa.csv')
#     with open('output.csv', mode='a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([f'fgl_hitters_{w}_pa', df.to_string(index=False)])
#
# for w in ipwindow:
#     df = pitchers_preprocessing(f'fgl_pitchers_{w}_ip.csv')
#     with open('output.csv', mode='a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([f'fgl_pitchers_{w}_ip', df.to_string(index=False)])
#
# for w in pitchdaywindow:
#     df = pitchers_preprocessing(f'fgl_pitchers_last_{w}.csv')
#     with open('output.csv', mode='a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([f'fgl_pitchers_last_{w}', df.to_string(index=False)])