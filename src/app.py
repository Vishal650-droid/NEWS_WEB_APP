import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.data_ingestion import fetch_all_news
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from src.data_ingestion  import fetch_all_news, save_raw, RSS_FEEDS
from src.preprocessing   import preprocess_dataframe, save_processed
from src.sentiment_model import analyse_sentiment
from src.topic_model     import fit_topic_model, get_topic_words, N_TOPICS

st.set_page_config(
    page_title="📰 Real-Time News Sentiment & Topic Monitor",
    page_icon="📰",
    layout="wide",
)

with st.sidebar:
    st.title("⚙️ Controls")

    selected_sources = st.multiselect(
        "Select News Sources",
        options=list(RSS_FEEDS.keys()),
        default=list(RSS_FEEDS.keys()),
    )

    max_articles = st.slider(
        "Max articles per source",
        min_value=5, max_value=50, value=20, step=5,
    )

    n_topics = st.slider(
        "Number of Topics",
        min_value=2, max_value=12, value=6, step=1,
    )

    fetch_button = st.button("🔄 Fetch & Analyse News", type="primary")

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown(
        """
        1. **Ingest** – Download live news from RSS feeds  
        2. **Preprocess** – Clean text (remove HTML, stopwords)  
        3. **Sentiment** – VADER scores each article  
        4. **Topic Model** – LDA groups articles by theme  
        5. **Visualise** – Charts & tables shown here  
        """
    )

if "df" not in st.session_state:
    st.session_state.df = None

if fetch_button:
    if not selected_sources:
        st.error("Please select at least one news source.")
    else:
        with st.spinner("Fetching live news..."):
            sources = {k: v for k, v in RSS_FEEDS.items() if k in selected_sources}

            df = fetch_all_news(sources=sources, max_per_source=max_articles)
            if df.empty:
                st.error("Could not fetch any articles. Check your internet connection.")
                st.stop()
            save_raw(df)

        with st.spinner("Cleaning text..."):
            df = preprocess_dataframe(df)

        with st.spinner("Analysing sentiment..."):
          
            df = analyse_sentiment(df)

        with st.spinner(f"Discovering {n_topics} topics with LDA..."):
           
            import src.topic_model as tm
            tm.N_TOPICS = n_topics
            tm.lda_model.n_components = n_topics
            df = fit_topic_model(df)

        save_processed(df)
        st.session_state.df = df
        st.success(f"✅ Done! Analysed {len(df)} articles.")


df = st.session_state.df

if df is None:
    # Show a welcome screen
    st.title("📰 Real-Time News Sentiment & Topic Monitor")
    st.markdown(
        """
        ### Welcome! 👋
        This dashboard fetches **live news**, analyses the **emotional tone**
        (positive / negative / neutral) of each article, and automatically
        **discovers recurring themes** using Machine Learning.

        **To get started → press the button in the sidebar ←**

        ---
        #### What you'll learn from this project:
        | Concept | What it is |
        |---|---|
        | RSS Ingestion | Collecting real-world data automatically |
        | Text Preprocessing | Cleaning raw text for ML models |
        | VADER Sentiment | Rule-based emotion detection |
        | LDA Topic Modeling | Unsupervised clustering of documents |
        | Streamlit | Building interactive ML dashboards |
        """
    )
    st.stop()


st.title("📰 Real-Time News Sentiment & Topic Monitor")

c1, c2, c3, c4 = st.columns(4)
c1.metric("📄 Total Articles",  len(df))
c2.metric("😊 Positive",        int((df["sentiment_label"] == "Positive").sum()))
c3.metric("😠 Negative",        int((df["sentiment_label"] == "Negative").sum()))
c4.metric("😐 Neutral",         int((df["sentiment_label"] == "Neutral").sum()))

st.markdown("---")


tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Sentiment Overview",
    "🔵 Topic Explorer",
    "☁️ Word Clouds",
    "📋 Raw Articles",
])


with tab1:
    st.subheader("Sentiment Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart of Positive / Negative / Neutral
        sent_counts = df["sentiment_label"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_pie = px.pie(
            sent_counts,
            names="Sentiment",
            values="Count",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Negative": "#e74c3c",
                "Neutral":  "#95a5a6",
            },
            title="Overall Sentiment Split",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart: sentiment by news source
        source_sent = (
            df.groupby(["source", "sentiment_label"])
              .size()
              .reset_index(name="count")
        )
        fig_bar = px.bar(
            source_sent,
            x="source",
            y="count",
            color="sentiment_label",
            barmode="stack",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Negative": "#e74c3c",
                "Neutral":  "#95a5a6",
            },
            title="Sentiment by Source",
            labels={"source": "News Source", "count": "Articles"},
        )
        fig_bar.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Compound score histogram
    st.subheader("Compound Score Distribution")
    st.markdown(
        "_Compound score ranges from -1 (most negative) to +1 (most positive). "
        "Values between -0.05 and +0.05 are classified as Neutral._"
    )
    fig_hist = px.histogram(
        df,
        x="sentiment_compound",
        nbins=40,
        color="sentiment_label",
        color_discrete_map={
            "Positive": "#2ecc71",
            "Negative": "#e74c3c",
            "Neutral":  "#95a5a6",
        },
        title="Distribution of Compound Sentiment Scores",
    )
    fig_hist.add_vline(x=0.05,  line_dash="dash", line_color="green")
    fig_hist.add_vline(x=-0.05, line_dash="dash", line_color="red")
    st.plotly_chart(fig_hist, use_container_width=True)



with tab2:
    st.subheader("Discovered Topics")
    st.markdown(
        "_LDA found these topic clusters automatically. The topic labels "
        "show the top 3 keywords._"
    )

    
    topic_words_dict = get_topic_words()

    
    for tid, words in topic_words_dict.items():
        topic_articles = df[df["topic_id"] == tid]
        with st.expander(
            f"**Topic {tid}** — {' / '.join(words[:3])}  "
            f"({len(topic_articles)} articles)"
        ):
            st.markdown(f"**Top keywords:** {', '.join(words)}")
        
            if not topic_articles.empty:
                for _, row in topic_articles.head(5).iterrows():
                    label_emoji = {"Positive": "😊", "Negative": "😠", "Neutral": "😐"}.get(
                        row["sentiment_label"], "❓"
                    )
                    st.markdown(f"- {label_emoji} {row['title']}")

    st.markdown("---")
    
    st.subheader("Topic × Sentiment Heatmap")
    heatmap_data = (
        df.groupby(["topic_label", "sentiment_label"])
          .size()
          .unstack(fill_value=0)
    )
    fig_heat = px.imshow(
        heatmap_data,
        color_continuous_scale="RdYlGn",
        title="Number of Articles per Topic × Sentiment",
        text_auto=True,
    )
    st.plotly_chart(fig_heat, use_container_width=True)


with tab3:
    st.subheader("Word Clouds by Sentiment")
    st.markdown("_Larger words appear more frequently in that sentiment category._")

    wc_cols = st.columns(3)
    for i, (label, col) in enumerate(zip(["Positive", "Neutral", "Negative"], wc_cols)):
        subset = df[df["sentiment_label"] == label]["clean_text"]
        text   = " ".join(subset.dropna().tolist())

        if text.strip():
            wc = WordCloud(
                width=400, height=300,
                background_color="white",
                colormap="RdYlGn" if label != "Negative" else "Reds",
                max_words=80,
            ).generate(text)

            fig, ax = plt.subplots(figsize=(5, 3))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(f"{label}", fontsize=14, fontweight="bold")
            col.pyplot(fig)
            plt.close(fig)
        else:
            col.info(f"No {label} articles found.")



with tab4:
    st.subheader("All Articles")

    # Filters
    filter_col1, filter_col2 = st.columns(2)
    sentiment_filter = filter_col1.multiselect(
        "Filter by Sentiment",
        ["Positive", "Negative", "Neutral"],
        default=["Positive", "Negative", "Neutral"],
    )
    source_filter = filter_col2.multiselect(
        "Filter by Source",
        df["source"].unique().tolist(),
        default=df["source"].unique().tolist(),
    )

    filtered = df[
        df["sentiment_label"].isin(sentiment_filter) &
        df["source"].isin(source_filter)
    ]

   
    display_cols = ["title", "source", "sentiment_label", "sentiment_compound",
                    "topic_label", "published"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].rename(columns={
            "sentiment_label":    "Sentiment",
            "sentiment_compound": "Score",
            "topic_label":        "Topic",
        }),
        use_container_width=True,
        height=450,
    )

    
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download as CSV",
        data=csv,
        file_name="news_analysis.csv",
        mime="text/csv",
    )
