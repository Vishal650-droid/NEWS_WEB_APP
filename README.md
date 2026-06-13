# The Sentiment Post 📰

An elegant, minimalist news aggregator dashboard heavily inspired by **The New York Times** editorial aesthetic. It pulls live global wires via RSS feeds and utilizes an underlying **VADER NLP Sentiment lexicon** pipeline to provide on-demand sentiment analysis.

To avoid trigger-heavy headlines or spoiler-heavy biases, sentiment analysis is never automated on page load—giving the user the unique agency to check the emotional composition of any article with a single click before reading.

##  Key Features
- **Live RSS Ingestion:** Dynamically aggregates articles from global dispatch streams (BBC, Reuters, Al Jazeera, and more).
- **On-Demand VADER Scoring:** Integrates a custom ML preprocessing and scoring module to compute precise metric weights (`Positive`, `Negative`, `Neutral`).
- **State Preservation:** Powered by robust UI state management to prevent structural reruns or stream resets upon click events.
- **Classic Editorial Design:** Complete dark-mode bypass layout tailored with typography scaling, deep double-rule borders, and subtle muted content badges.

## 📂 Project Architecture
```text
News_sentiment_web_app/
│
├── src/                       # Machine Learning Core Logic
│   ├── __init__.py
│   ├── app.py                 # Core ML entry
│   ├── data_ingestion.py      # Raw ingestion utilities
│   ├── preprocessing.py       # Custom NLP tokenization & text cleaning
│   ├── run_pipeline.py        # Mass data streaming pipeline
│   ├── sentiment_model.py     # VADER scoring & evaluation model
│   ├── topic_model.py         # Latent topic monitoring
│   └── utils.py               # Custom operational loggers
│
├── streamlit_app.py           # Editorial Frontend User Interface
├── requirements.txt           # App Dependencies
└── .gitignore                 # Track protection rule definitions