
import re
import nltk
import pandas as pd
from src.utils import get_logger

logger = get_logger(__name__)

def download_nltk_data():
    resources = ["stopwords", "wordnet", "omw-1.4", "punkt"]
    for r in resources:
        try:
            nltk.download(r, quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK resource '{r}': {e}")

download_nltk_data()

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

STOP_WORDS = set(stopwords.words("english"))

CUSTOM_STOPWORDS = {
    "said", "says", "say", "also", "would", "could", "one",
    "two", "three", "new", "year", "years", "time", "day",
    "week", "month", "people", "man", "woman", "http", "www",
}
STOP_WORDS.update(CUSTOM_STOPWORDS)

lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Cleans a single raw text string.

    Args:
        text (str): Raw article title/summary text.

    Returns:
        str: Cleaned text as a space-joined string of tokens.
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return ""

    text = text.lower()

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"http\S+|www\S+", " ", text)

    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = word_tokenize(text)

    tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in STOP_WORDS and len(token) > 2
    ]

    return " ".join(tokens)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies clean_text() to every article in the DataFrame.
    Adds a new column 'clean_text' with the cleaned result.

    Args:
        df (pd.DataFrame): Raw articles from data_ingestion.

    Returns:
        pd.DataFrame: Same DataFrame with 'clean_text' added.
    """
    if df.empty:
        logger.warning("Empty DataFrame passed to preprocess_dataframe.")
        return df

    logger.info("Cleaning text for all articles...")

    df["clean_text"] = df["text"].apply(clean_text)

    before = len(df)
    df = df[df["clean_text"].str.len() > 10].reset_index(drop=True)
    after = len(df)

    logger.info(f"Dropped {before - after} empty articles after cleaning.")
    logger.info(f"Preprocessing complete. {after} articles ready.")

    return df


def save_processed(df: pd.DataFrame, processed_dir: str = "data/processed") -> str:
    import os
    os.makedirs(processed_dir, exist_ok=True)
    filepath = f"{processed_dir}/articles_processed.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Processed data saved → {filepath}")
    return filepath


if __name__ == "__main__":
    sample = "Breaking News: Scientists discovered <b>new</b> method to fight COVID-19! Visit https://example.com"
    print("RAW:    ", sample)
    print("CLEAN:  ", clean_text(sample))
