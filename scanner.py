import pandas as pd

url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

df = pd.read_csv(url)

print(f"Total NSE stocks loaded: {len(df)}")
