from pandasgui import show
import pandas as pd

df = pd.read_csv('enobounceback.csv')
gui = show(df)