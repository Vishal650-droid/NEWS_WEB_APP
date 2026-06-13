
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_ingestion  import fetch_all_news, save_raw
from src.preprocessing   import preprocess_dataframe, save_processed
from src.sentiment_model import analyse_sentiment
from src.topic_model     import fit_topic_model, get_topic_words
from src.utils           import get_logger

logger = get_logger("pipeline")

def run():
    logger.info("=" * 60)
    logger.info("STARTING FULL PIPELINE")
    logger.info("=" * 60)

    logger.info("[1/4] Fetching news from RSS feeds...")
    df = fetch_all_news(max_per_source=15)
    save_raw(df)
    logger.info(f"      Articles fetched: {len(df)}")

    logger.info("[2/4] Preprocessing text...")
    df = preprocess_dataframe(df)

    logger.info("[3/4] Running sentiment analysis...")
    df = analyse_sentiment(df)

    logger.info("[4/4] Running topic modeling (LDA)...")
    df = fit_topic_model(df)
    save_processed(df)

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Total articles: {len(df)}")
    logger.info("Sentiment distribution:")
    print(df["sentiment_label"].value_counts().to_string())
    logger.info("\nTop topic words:")
    for tid, words in get_topic_words().items():
        logger.info(f"  Topic {tid}: {', '.join(words[:5])}")
    logger.info("=" * 60)

    return df

if __name__ == "__main__":
    df = run()
    print("\nFirst 5 articles:")
    print(df[["title", "sentiment_label", "topic_label"]].head())
