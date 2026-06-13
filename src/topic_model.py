
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from src.utils import get_logger

logger = get_logger(__name__)


N_TOPICS       = 6     
N_TOP_WORDS    = 10    
MAX_FEATURES   = 1000  
MAX_ITER       = 15    

count_vectorizer = CountVectorizer(
    max_features=MAX_FEATURES,
    max_df=0.90,    
    min_df=2,       
    ngram_range=(1, 2),  
)

lda_model = LatentDirichletAllocation(
    n_components=N_TOPICS,
    random_state=42,          
    max_iter=MAX_ITER,
    learning_method="online",
    n_jobs=-1,                
)


def fit_topic_model(df: pd.DataFrame) -> pd.DataFrame:
    
    if df.empty or "clean_text" not in df.columns:
        logger.error("DataFrame must have 'clean_text' column.")
        return df

    texts = df["clean_text"].tolist()
    logger.info(f"Fitting LDA on {len(texts)} articles with {N_TOPICS} topics...")

    doc_term_matrix = count_vectorizer.fit_transform(texts)
    logger.info(f"Doc-Term Matrix shape: {doc_term_matrix.shape}")

    doc_topic_matrix = lda_model.fit_transform(doc_term_matrix)

    df["topic_id"] = np.argmax(doc_topic_matrix, axis=1)

    df["topic_confidence"] = doc_topic_matrix.max(axis=1).round(3)

    logger.info("LDA fitting complete. Extracting top words per topic...")

    topic_words = get_topic_words(lda_model, count_vectorizer)

    for tid, words in topic_words.items():
        logger.info(f"  Topic {tid}: {', '.join(words)}")

    df["topic_label"] = df["topic_id"].apply(
        lambda tid: " / ".join(topic_words[tid][:3])
    )

    return df


def get_topic_words(model=None, vectorizer=None) -> dict:
    
    if model is None:
        model = lda_model
    if vectorizer is None:
        vectorizer = count_vectorizer

    feature_names = vectorizer.get_feature_names_out()
    topic_words = {}

    for topic_idx, topic_vec in enumerate(model.components_):
        top_indices = topic_vec.argsort()[-N_TOP_WORDS:][::-1]
        top_words   = [feature_names[i] for i in top_indices]
        topic_words[topic_idx] = top_words

    return topic_words


if __name__ == "__main__":
    sample_data = {
        "clean_text": [
            "election vote party campaign president candidate poll",
            "stock market economy inflation rate federal reserve",
            "covid vaccine hospital health patient doctor",
            "football match score goal player team league",
            "technology ai robot machine learning algorithm data",
            "war army soldier attack military bomb missile",
            "election candidate campaign vote party poll result",
            "stock price trade market economy recession inflation",
            "health hospital vaccine covid patient drug trial",
        ]
    }
    df = pd.DataFrame(sample_data)
    df = fit_topic_model(df)
    print(df[["clean_text", "topic_id", "topic_label", "topic_confidence"]])
