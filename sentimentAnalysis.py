import numpy as np
import pandas as pd
import os
from time import gmtime, strftime

from stockSentiment import getSentiment 

def createDF(pages=1, num_articles=10):
    df = pd.DataFrame.from_dict(getSentiment(pages, num_articles), orient='index')
    df.index.name = 'ticker'
    return df

def saveDF(output_path, df=createDF(1, 10)) -> None:
    os.makedirs(output_path, exist_ok=True)
    current_time = strftime("%Y-%m-%d-%H%M%S", gmtime())
    csv_path = os.path.join(output_path, f"{current_time}_sentiment.csv")
    df.to_csv(csv_path)

saveDF(output_path='results/', df=createDF(5,500))

#volatility - high 