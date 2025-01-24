import configparser
import json
import requests
import numpy as np
import pandas as pd

config = configparser.ConfigParser()
config.read("config.ini")

def FMPUrl(page=0, num_articles=1):
    key = config.get('FMP','API_KEY')
    return f'https://financialmodelingprep.com/api/v3/fmp/articles?page={page}&size={num_articles}&apikey={key}'

def splitTicker(ticker):
    return ticker.split(':')[1] if ':' in ticker else ticker

def getData(pages, num_articles):
    fetched = []
    tickers = []
    for page in range(pages):
        response = requests.get(FMPUrl(page=page, num_articles=num_articles)).json()
        content = response['content']
        for article in content:
            fetched.append(article)
            tickers.append(splitTicker(article['tickers']))
    return fetched, tickers

_, tickers = getData(1,1)
print(tickers)