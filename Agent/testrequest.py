import requests
import pandas as pd
import json
# import os

# from cassandra.cluster import Cluster
# from cassandra.auth import PlainTextAuthProvider
#
# data_path = 'D:\Git_desktop\BigDataStockAnalyzer\Agent\PriceHistory'
#
# for file in os.listdir(data_path):
#     if file.endswith('.json'):
#         file_path = os.path.join(data_path, file)
#
#         with open(file_path, 'r') as file:
#             ticker_data = json.load(file)

# df = pd.read_csv('TWTR.csv')
# # df.head()
#
# close = df['Close'].tolist()
# volume = df['Volume'].tolist()
#
# output = []
#
# for i in range(200):
#     data = json.dumps([close[i], volume[i]])
#     requested = requests.get('http://localhost:8005/trade?data=' + data).json()
#     output.append(requested)
#
# with open('output.json', 'w') as outfile:
#     json.dump(output, outfile)

requested = requests.get('http://127.0.0.1:8005/setticker?args='+'A32.json').json()
print(requested)