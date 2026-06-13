
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.utils import get_logger

logger = get_logger(__name__)

analyser = SentimentIntensityAnalyzer()


def get_sentiment_scores(text: str) -> dict:
   
    if not isinstance(text, str) or len(text.strip()) == 0:
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0, "label": "Neutral"}

    scores = analyser.polarity_scores(text)

    compound = scores["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    scores["label"] = label
    return scores


def analyse_sentiment(df: pd.DataFrame) -> pd.DataFrame:
   
    if df.empty:
        logger.warning("Empty DataFrame passed to analyse_sentiment.")
        return df

    logger.info("Running VADER sentiment analysis...")

    scores_series = df["text"].apply(get_sentiment_scores)

    scores_df = pd.json_normalize(scores_series)
    scores_df.columns = [f"sentiment_{c}" for c in scores_df.columns]

    df = pd.concat([df.reset_index(drop=True), scores_df], axis=1)

    counts = df["sentiment_label"].value_counts()
    logger.info(f"Sentiment distribution:\n{counts.to_string()}")

    return df


if __name__ == "__main__":
    tests = [
        "Scientists discover a MAJOR breakthrough in cancer treatment!",
        "Devastating flood kills hundreds in southern region",
        "Prime Minister attends conference on trade policy",
        "Stock market CRASHES as inflation fears rise!!!",
    ]
    for t in tests:
        result = get_sentiment_scores(t)
        print(f"[{result['label']:8s}  {result['compound']:+.2f}]  {t}")
