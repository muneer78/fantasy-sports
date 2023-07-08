import pandas as pd
import re

dfsched = pd.read_excel('roster-resource-download.xlsx', usecols = [0,1])
dfprops = pd.read_csv('FanGraphs Leaderboard(9).csv')

dfsched.rename(columns={dfsched.columns[1]: 'Name'}, inplace=True)
dfsched = dfsched.fillna(0)

def delete_first_line(cell_value):
    lines = cell_value.split('\n')
    if len(lines) > 1:
        lines.pop(0)
    return '\n'.join(lines)

dfsched = dfsched.applymap(delete_first_line)

def remove_text(cell_value):
    pattern = r'\s*\(R\)|\s*\(L\)'
    return re.sub(pattern, '', cell_value)

dfsched = dfsched.applymap(remove_text)
dfsched['Name'] = dfsched['Name'].str.strip()

dfsortedBB = dfprops.sort_values('BB%+', ascending=True)
dfbbtop25 = dfsortedBB.head(25).fillna(0)

dfsortedK = dfprops.sort_values('K%+', ascending=False)
dfktop25 = dfsortedK.head(25).fillna(0)

matching_dfbbtop25 = dfsched[dfsched['Name'].isin(dfbbtop25['Name'])]
matching_dfktop25 = dfsched[dfsched['Name'].isin(dfktop25['Name'])]

matching_dfktop25 = pd.merge(matching_dfktop25, dfktop25[['Name', 'K%+', 'BB%+']], on='Name', how='left')
matching_dfbbtop25 = pd.merge(matching_dfbbtop25, dfbbtop25[['Name', 'K%+', 'BB%+']], on='Name', how='left')

print("Low walk props to explore:")
print(matching_dfbbtop25)
print(" ")
print("High strikeout props to explore:")
print(matching_dfktop25)