import configparser
import requests
import time
import torch
import scipy
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

config = configparser.ConfigParser()
config.read("config.ini")


def FMPUrl(page=0, num_articles=1):
    key = config.get("FMP", "API_KEY")
    return f"https://financialmodelingprep.com/api/v3/fmp/articles?page={page}&size={num_articles}&apikey={key}"


def splitTicker(ticker):
    return ticker.split(":")[1] if ":" in ticker else ticker


def GroupContentByStock(func):
    def wrapper(*args, **params):
        tickers, articles, stocks = func(*args, **params)
        data = {stock: [] for stock in stocks}
        for stock, article in zip(stocks, articles):
            soup = BeautifulSoup(article, "html.parser")
            data[stock] += [
                paragraph.get_text() for paragraph in soup.find_all("p")
            ]  # for each stock, append all paragraphs where it is mentioned
        return data

    return wrapper


@GroupContentByStock
def getData(pages, num_articles):
    fetched = []
    stocks = []
    for page in tqdm(range(pages), "Fetching pages"):
        response = requests.get(FMPUrl(page=page, num_articles=num_articles)).json()
        content = response["content"]
        stocks += [splitTicker(article["tickers"]) for article in content]
        fetched += [article["content"] for article in content]
        time.sleep(0.5)
    tickers = list(set(stocks))
    return tickers, fetched, stocks


def getSentiment(pages, num_articles, opinion_treshhold=0.8):
    data = getData(pages=pages, num_articles=num_articles)
    stocks = list(data.keys())
    result = {
        stock: {"negative": 0, "neutral": 0, "positive": 0, "fact": 0, "opinion": 0}
        for stock in stocks
    }
    tokenizer_kwargs = {"padding": True, "truncation": True, "max_length": 512}

    for ticker in tqdm(data.keys(), "Processing tickers"):
        for paragraph in data[ticker]:
            with torch.no_grad():
                inputs = tokenizer(paragraph, return_tensors="pt", **tokenizer_kwargs)
                outputs = model(**inputs)
                probabilities = scipy.special.softmax(outputs.logits.numpy().squeeze())

                sentiment = model.config.id2label[probabilities.argmax()]
                result[ticker][sentiment.lower()] += (
                    1  # sentiment is label 'positive', 'negative' or 'neutral'. lower to match results setup
                )

                max_prob = probabilities.max()
                if max_prob >= opinion_treshhold and sentiment.lower() != "neutral":
                    result[ticker]["opinion"] += 1
                else:
                    result[ticker]["fact"] += 1
    return result
