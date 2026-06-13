import feedparser
import pandas as pd
from datetime import datetime
from src.utils import get_logger, ensure_dir, save_json

logger = get_logger(__name__)

RSS_FEEDS = {
    "BBC News":         "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters":          "https://feeds.reuters.com/reuters/topNews",
    "Al Jazeera":       "https://www.aljazeera.com/xml/rss/all.xml",
    "The Hindu":        "https://www.thehindu.com/news/national/?service=rss",
    "NPR News":         "https://feeds.npr.org/1001/rss.xml",
    "TechCrunch":       "https://techcrunch.com/feed/",
    "Ars Technica":     "https://feeds.arstechnica.com/arstechnica/index",
}


def fetch_all_news(sources: dict = RSS_FEEDS, max_per_source: int = 20) -> pd.DataFrame:
    
    all_articles = []

    for source_name, url in sources.items():
        logger.info(f"Fetching from {source_name} ...")
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:max_per_source]:
                article = {
                    "title":     entry.get("title", "").strip(),
                    "summary":   entry.get("summary", "").strip(),
                    "text":      (entry.get("title", "") + " " +
                                  entry.get("summary", "")).strip(),
                    "link":      entry.get("link", ""),
                    "published": _parse_date(entry),
                    "source":    source_name,
                }
                all_articles.append(article)

            logger.info(f"  ✓ Got {min(len(feed.entries), max_per_source)} articles")

        except Exception as e:
            
            logger.warning(f"  ✗ Failed to fetch {source_name}: {e}")

    if not all_articles:
        logger.error("No articles fetched. Check your internet connection.")
        return pd.DataFrame()

    df = pd.DataFrame(all_articles)

    
    df = df[df["title"].str.len() > 0].reset_index(drop=True)

    logger.info(f"Total articles collected: {len(df)}")
    return df


def _parse_date(entry) -> str:
    
    try:
        # published_parsed is a time.struct_time object
        t = entry.get("published_parsed")
        if t:
            return datetime(*t[:6]).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    # Fallback: use now
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



def save_raw(df: pd.DataFrame, raw_dir: str = "data/raw") -> str:
   
    ensure_dir(raw_dir)
    filepath = f"{raw_dir}/articles_raw.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Raw data saved → {filepath}")
    return filepath


if __name__ == "__main__":
    df = fetch_all_news()
    print(df.head())          
    print(df.shape)             
    save_raw(df)
