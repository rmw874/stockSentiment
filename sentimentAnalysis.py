import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from time import gmtime, strftime
from adjustText import adjust_text

from stockSentiment import getSentiment


def createDF(pages=1, num_articles=10):
    df = pd.DataFrame.from_dict(getSentiment(pages, num_articles), orient="index")
    df.index.name = "ticker"
    return df


def saveDF(output_path, df) -> None:
    os.makedirs(output_path, exist_ok=True)
    current_time = strftime("%Y-%m-%d-%H%M%S", gmtime())
    csv_path = os.path.join(output_path, f"{current_time}_sentiment.csv")
    df.to_csv(csv_path)
    fig = plot_market_psychology(df)
    plt.savefig(
        f"{output_path}/{current_time}_market_psychology.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def normalize(series):
    norm = (series - series.min()) / (series.max() - series.min())
    return norm.round(4)


def addPolarizationMetrics(df):
    df["volume"] = df["fact"] + df["opinion"]
    df["conviction"] = normalize(df["opinion"] / df["volume"]).round(4)
    df["extremity"] = df.apply(
        lambda row: 1.0
        if row["neutral"] == 0 and row["volume"] > 0
        else 1 / row["neutral"]
        if row["neutral"] > 0
        else 0,
        axis=1,
    ).round(4)
    return df


def plot_market_psychology(df):
    # todo: update depending on dataset distribution
    df = df[df["volume"] >= 50]
    df = df[df["volume"] <= 500]

    sns.set_style("whitegrid")
    sns.set_palette("deep")
    plt.figure(figsize=(12, 8))
    plt.title("Market Psychology Analysis")

    scatter = plt.scatter(
        df["volume"],
        df["conviction"],
        c=df["extremity"],
        cmap="YlOrRd",
        alpha=0.6,
        s=100,
    )

    plt.colorbar(scatter, label="Extremity Score")

    plt.xlabel("Volume of paragraphs")
    plt.ylabel("Conviction Score")

    volume_threshold = df["volume"].quantile(0.8)
    conviction_threshold = df["conviction"].quantile(0.8)

    for idx, row in df.iterrows():
        if row["volume"] > volume_threshold or row["conviction"] > conviction_threshold:
            # plt.annotate(row['ticker'], #used if reading csv. idx used if df hasn't been transformed
            plt.annotate(
                idx,
                (row["volume"], row["conviction"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
            )

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    return plt


df_test = addPolarizationMetrics(createDF(7, 500))
saveDF(output_path="results/", df=df_test)

# test = pd.read_csv('results/2025-01-24-220835_sentiment.csv')
# fig = plot_market_psychology(test)
# plt.savefig('market_psychology_1.png', dpi=300, bbox_inches='tight')
# plt.close()
