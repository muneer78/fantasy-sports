import pandas as pd

#hitters = pd.ExcelFile('Hitters.xlsx')
#pitchers = pd.ExcelFile('Pitchers.xlsx')

hitters='Hitters.xlsx'
pitchers='Pitchers.xlsx'

df1 = pd.read_excel(hitters,sheetname='CT_lot4_LDO_3Tbin1')

merge= hitters.merge(pitchers[['Total Z-Score']])

print(merge)