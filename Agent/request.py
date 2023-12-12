import requests
import pandas as pd
import json

df = pd.read_csv('TWTR.csv')
# df.head()

close = df['Close'].tolist()
volume = df['Volume'].tolist()

for i in range(200):
    data = json.dumps([close[i], volume[i]])
    requested = requests.get('http://localhost:8005/trade?data=' + data).json()
    print(requested)