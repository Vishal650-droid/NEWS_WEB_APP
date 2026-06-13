"""
The Sentiment Post — NYT-inspired News Sentiment Dashboard
============================================================
Root-level entry point. Sentiment logic imported from src.sentiment_model.

Run with:
    streamlit run streamlit_app.py
"""

# ── stdlib ─────────────────────────────────────────────────────────────────────
import re
import sys
import os
from datetime import datetime

# ── third-party ────────────────────────────────────────────────────────────────
import streamlit as st
import feedparser

# ── path: make the project root importable so `from src.sentiment_model import …`
#    resolves regardless of the working directory used to launch streamlit.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ── project import ─────────────────────────────────────────────────────────────
from src.sentiment_model import get_sentiment_scores   # noqa: E402


# ══════════════════════════════════════════════════════════════════════════════
#  RSS FEED REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

RSS_FEEDS: dict[str, str] = {
    "BBC News":     "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters":      "https://feeds.reuters.com/reuters/topNews",
    "Al Jazeera":   "https://www.aljazeera.com/xml/rss/all.xml",
    "The Hindu":    "https://www.thehindu.com/news/national/?service=rss",
    "NPR News":     "https://feeds.npr.org/1001/rss.xml",
    "TechCrunch":   "https://techcrunch.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
}


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be the first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="The Sentiment Post",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Overrides System Dark Mode for an Authentic Editorial Look
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    /* ── Fonts ────────────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');

    /* ── High-Specificity Light Theme Force ──────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        background-color: #faf9f7 !important;
        color: #121212 !important;
        font-family: 'Source Sans 3', Arial, sans-serif;
    }

    /* Force all text elements in main content area to read beautifully */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #121212 !important;
    }

    /* Clear header block */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    #MainMenu, footer { visibility: hidden; }
    
    .block-container {
        padding-top: 1rem !important;
        max-width: 1180px !important;
    }

    /* ── Dark Sidebar for striking contrast ───────────────────────────────── */
    /* ── Light Sidebar for unified newspaper theme ────────────────────────── */
    /* ── Light Sidebar for unified newspaper theme ────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #f1ece4 !important; /* Muted warm paper tone for clean division */
        border-right: 1px solid #ddd !important;
    }
    
    /* Target specific text containers instead of using '*' which breaks internal icons */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSlider div {
        color: #121212 !important;
        font-family: 'Source Sans 3', sans-serif !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #121212 !important;
        font-family: 'Playfair Display', Georgia, serif !important;
        letter-spacing: 0.02em;
    }
    [data-testid="stSidebar"] .stCheckbox label {
        color: #121212 !important;
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    
    /* Force hide the leaking keyboard shortcut helper tag entirely */
    [data-testid="stSidebar"] kbd {
        display: none !important;
    }

    /* ── Sidebar Fetch Button (Light Mode) ────────────────────────────────── */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #121212 !important;
        border-radius: 0 !important;
        padding: 0.55rem 1.2rem !important;
        margin-top: 0.5rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #121212 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #121212 !important;
        border-color: #8a6a2a !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover * {
        color: #faf9f7 !important;
    }
    
    /* Small info text at the sidebar bottom */
    [data-testid="stSidebar"] small, [data-testid="stSidebar"] small strong {
        color: #444444 !important;
    }

    /* ── Dropdowns and Multi-select Inputs Visibility Fixing ────────────── */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #121212 !important;
        border: 1px solid #ccc !important;
    }
    
    /* Dropdown list popup containers */
    div[data-testid="stSelectbox"] ul, div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        color: #121212 !important;
    }
    
    /* Selected pills/tags inside multi-select */
    span[data-baseweb="tag"] {
        background-color: #e2ede4 !important;
        color: #121212 !important;
        border: 1px solid #b5ccb8 !important;
    }

    /* ── Masthead ─────────────────────────────────────────────────────────── */
    .masthead {
        text-align: center;
        padding: 1.6rem 0 0.6rem 0;
        border-bottom: 3px double #121212;
        margin-bottom: 0;
    }
    .masthead-dateline {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #555555 !important;
        margin-bottom: 0.35rem;
    }
    .masthead-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: clamp(2.4rem, 5vw, 4rem);
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #0a0a0a !important;
        line-height: 1;
        margin: 0;
    }
    .masthead-tagline {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #555555 !important;
        margin-top: 0.4rem;
        font-style: italic;
    }
    .masthead-rule {
        border: none;
        border-top: 1px solid #121212;
        margin: 0.55rem 0 0 0;
    }

    /* ── Section Label ────────────────────────────────────────────────────── */
    .section-label {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #444444 !important;
        border-bottom: 2px solid #121212;
        padding-bottom: 0.3rem;
        margin: 1.6rem 0 1rem 0;
    }

    /* ── Article Card ─────────────────────────────────────────────────────── */
    .article-card {
        border-bottom: 1px solid #ddd;
        padding: 1.1rem 0 0.8rem 0;
        margin-bottom: 0;
    }
    .article-meta {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #8a6a2a !important;
        margin-bottom: 0.35rem;
    }
    .article-headline {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.3;
        color: #0a0a0a !important;
        margin: 0 0 0.45rem 0;
    }
    .article-snippet {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.92rem;
        line-height: 1.65;
        color: #252525 !important;
        margin-bottom: 0.5rem;
        font-weight: 400;
    }
    .article-link {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #1a1a1a !important;
        text-decoration: underline;
        text-underline-offset: 3px;
    }
    .article-link:hover { color: #8a6a2a !important; }

    /* ── Sentiment Badges ─────────────────────────────────────────────────── */
    .sentiment-positive {
        display: inline-block;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #137333 !important;
        border: 1px solid #137333;
        padding: 0.18rem 0.65rem;
        background-color: #e6f4ea;
        margin-right: 0.5rem;
        font-weight: 600;
    }
    .sentiment-negative {
        display: inline-block;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #c5221f !important;
        border: 1px solid #c5221f;
        padding: 0.18rem 0.65rem;
        background-color: #fce8e6;
        margin-right: 0.5rem;
        font-weight: 600;
    }
    .sentiment-neutral {
        display: inline-block;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #444444 !important;
        border: 1px solid #777777;
        padding: 0.18rem 0.65rem;
        background-color: #f1f3f4;
        margin-right: 0.5rem;
        font-weight: 600;
    }
    .sentiment-score {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.68rem;
        color: #555555 !important;
        letter-spacing: 0.06em;
        vertical-align: middle;
    }

    /* ── Interactive Newsprint Action Buttons ───────────────────────────── */
    /* ── Inline "Check Sentiment" button ─────────────────────────────────── */
    .stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #121212 !important;
        border-radius: 0 !important;
        padding: 0.3rem 0.9rem !important;
        transition: all 0.15s ease;
    }
    
    /* Default button text state */
    .stButton > button * {
        color: #121212 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
    }
    
    /* Hover, Active, and Focus States */
    .stButton > button:hover, .stButton > button:active, .stButton > button:focus {
        border-color: #8a6a2a !important;
        background-color: #121212 !important;
    }
    
    /* Crucial Fix: Force all inner text elements to invert to crisp white on hover */
    .stButton > button:hover *, .stButton > button:active *, .stButton > button:focus * {
        color: #faf9f7 !important;
    }

    /* ── Stats Bar ────────────────────────────────────────────────────────── */
    .stats-bar {
        display: flex;
        gap: 2rem;
        padding: 0.8rem 0;
        border-top: 1px solid #121212;
        border-bottom: 1px solid #121212;
        margin: 0.6rem 0 0 0;
    }
    .stat-item { text-align: left; }
    .stat-value {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #0a0a0a !important;
        line-height: 1;
    }
    .stat-label {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #555555 !important;
        margin-top: 0.15rem;
    }
    .stat-divider {
        width: 1px;
        background: #121212;
        align-self: stretch;
    }

    /* ── Welcome Screen ───────────────────────────────────────────────────── */
    .welcome-body {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1rem;
        line-height: 1.75;
        color: #222222 !important;
        max-width: 640px;
        margin: 2rem auto;
        font-weight: 400;
    }
    .welcome-em {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 1.45rem;
        color: #0a0a0a !important;
        line-height: 1.5;
        border-left: 3px solid #8a6a2a;
        padding-left: 1rem;
        margin: 1.8rem 0;
    }

    /* ── Source Pill Tag ──────────────────────────────────────────────────── */
    .source-pill {
        display: inline-block;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8a6a2a !important;
        border: 1px solid #c8a96a;
        padding: 0.12rem 0.5rem;
        margin-right: 0.4rem;
        vertical-align: middle;
        background-color: #ffffff;
    }

    /* ── Layout Rules ─────────────────────────────────────────────────────── */
    .no-results {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.88rem;
        color: #555555 !important;
        font-style: italic;
        padding: 1.5rem 0;
        text-align: center;
    }
    .card-sep {
        border: none;
        border-top: 1px solid #ddd;
        margin: 0 0 0.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _strip_html(raw: str) -> str:
    """Remove all HTML tags from *raw* and return plain text."""
    return re.sub(r"<[^>]+>", "", raw or "").strip()


def _truncate(text: str, n: int = 200) -> str:
    """Truncate *text* to at most *n* chars, breaking cleanly on a word boundary."""
    text = _strip_html(text)
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def _parse_date(entry) -> str:
    """
    Extract a publication date string from a feedparser entry.
    Returns 'YYYY-MM-DD HH:MM:SS', falling back to the current timestamp.
    """
    try:
        t = entry.get("published_parsed")
        if t:
            return datetime(*t[:6]).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _fetch_feed(source_name: str, url: str, max_items: int) -> list[dict]:
    """
    Fetch one RSS feed and return a list of article dicts.
    Network/parse failures become sidebar warnings, not raised exceptions.
    """
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:max_items]:
            title   = _strip_html(entry.get("title",   ""))
            summary = _strip_html(entry.get("summary", ""))
            articles.append(
                {
                    "title":     title,
                    "summary":   summary,
                    "text":      f"{title} {summary}".strip(),
                    "link":      entry.get("link", "#"),
                    "published": _parse_date(entry),
                    "source":    source_name,
                }
            )
        return articles
    except Exception as exc:
        st.sidebar.warning(f"⚠ {source_name}: {exc}")
        return []


def _sentiment_tag_html(result: dict) -> str:
    """Return an HTML string with an editorial sentiment badge + compound score."""
    label   = result["label"]
    score   = result["compound"]
    css_cls = {
        "Positive": "sentiment-positive",
        "Negative": "sentiment-negative",
        "Neutral":  "sentiment-neutral",
    }.get(label, "sentiment-neutral")
    return (
        f'<span class="{css_cls}">{label}</span>'
        f'<span class="sentiment-score">compound {score:+.3f}</span>'
    )


def _today_dateline() -> str:
    """Return today's date as an all-caps editorial dateline."""
    return datetime.now().strftime("%A, %B %-d, %Y").upper()


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════════════════════════

if "articles"   not in st.session_state:
    st.session_state.articles   = []   # list[dict] — fetched articles
if "sentiments" not in st.session_state:
    st.session_state.sentiments = {}   # {article_idx: sentiment_result_dict}
if "fetched_at" not in st.session_state:
    st.session_state.fetched_at = None


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — source checkboxes, article-count slider, fetch trigger
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### The Sentiment Post")
    st.markdown("---")

    st.markdown("**Sources**")
    selected_sources: list[str] = []
    for src_name in RSS_FEEDS:
        if st.checkbox(src_name, value=True, key=f"chk_{src_name}"):
            selected_sources.append(src_name)

    st.markdown("---")
    max_per: int = st.slider(
        "Articles per source", min_value=5, max_value=30, value=10, step=5
    )

    fetch_btn: bool = st.button("↻  Fetch Latest News")

    if st.session_state.fetched_at:
        st.markdown(
            f"<small style='color:#888'>Last fetched: "
            f"{st.session_state.fetched_at}</small>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
        <small style='color:#666;line-height:1.7'>
        Sentiment scored with <strong>VADER</strong> — a lexicon-rule model
        calibrated for news and social text.<br><br>
        Compound &ge;&nbsp;0.05 → Positive<br>
        Compound &le;&nbsp;&minus;0.05 → Negative<br>
        Otherwise → Neutral
        </small>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH LOGIC
# ══════════════════════════════════════════════════════════════════════════════

if fetch_btn:
    if not selected_sources:
        st.error("Please select at least one news source in the sidebar.")
    else:
        with st.spinner("Gathering dispatches from the wire…"):
            all_articles: list[dict] = []
            for src in selected_sources:
                all_articles.extend(_fetch_feed(src, RSS_FEEDS[src], max_per))

        if not all_articles:
            st.error(
                "No articles could be retrieved. "
                "Check your internet connection and try again."
            )
        else:
            st.session_state.articles   = all_articles
            st.session_state.sentiments = {}   # clear stale results on fresh fetch
            st.session_state.fetched_at = datetime.now().strftime("%H:%M:%S")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MASTHEAD  — always rendered
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f"""
    <div class="masthead">
        <div class="masthead-dateline">{_today_dateline()}</div>
        <h1 class="masthead-title">The Sentiment Post</h1>
        <div class="masthead-tagline">All the news, measured to the decimal</div>
        <hr class="masthead-rule"/>
    </div>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  WELCOME SCREEN  (shown before first fetch)
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state.articles:
    st.markdown(
        """
        <div class="welcome-body">
            <div class="welcome-em">
                "Journalism is printing what someone else does not want printed.
                Everything else is public relations."
            </div>
            Welcome to <strong>The Sentiment Post</strong> — a live editorial
            dashboard that reads from seven international wires, then lets you probe
            the emotional tone of any headline on demand.<br><br>
            Select your sources in the left panel and press
            <strong>↻ Fetch Latest News</strong> to begin.
            Sentiment is never run automatically — click per article when you're ready.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  STATS BAR
# ══════════════════════════════════════════════════════════════════════════════

articles:   list[dict] = st.session_state.articles
sentiments: dict       = st.session_state.sentiments

n_total    = len(articles)
n_analyzed = len(sentiments)
n_positive = sum(1 for v in sentiments.values() if v["label"] == "Positive")
n_negative = sum(1 for v in sentiments.values() if v["label"] == "Negative")
n_neutral  = sum(1 for v in sentiments.values() if v["label"] == "Neutral")

st.markdown(
    f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{n_total}</div>
            <div class="stat-label">Articles Loaded</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-value">{n_analyzed}</div>
            <div class="stat-label">Analysed</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-value" style="color:#137333">{n_positive}</div>
            <div class="stat-label">Positive</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-value" style="color:#c5221f">{n_negative}</div>
            <div class="stat-label">Negative</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-value" style="color:#444444">{n_neutral}</div>
            <div class="stat-label">Neutral</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  FILTER & SORT BAR
# ══════════════════════════════════════════════════════════════════════════════

all_sources = sorted({a["source"] for a in articles})

fcol1, fcol2, fcol3 = st.columns([2, 2, 1])

with fcol1:
    src_filter: list[str] = st.multiselect(
        "Filter by source",
        options=all_sources,
        default=all_sources,
        key="src_filter",
        label_visibility="collapsed",
        placeholder="All sources",
    )

with fcol2:
    sent_filter: list[str] = st.multiselect(
        "Filter by sentiment",
        options=["Positive", "Negative", "Neutral", "Not analysed"],
        default=["Positive", "Negative", "Neutral", "Not analysed"],
        key="sent_filter",
        label_visibility="collapsed",
        placeholder="All sentiments",
    )

with fcol3:
    sort_by: str = st.selectbox(
        "Sort",
        ["Date (newest)", "Date (oldest)", "Source A–Z"],
        label_visibility="collapsed",
        key="sort_by",
    )


def _sentiment_bucket(idx: int) -> str:
    """Return the scored sentiment label for *idx*, or 'Not analysed'."""
    return sentiments[idx]["label"] if idx in sentiments else "Not analysed"


active_sources = src_filter  or all_sources
active_labels  = sent_filter or ["Positive", "Negative", "Neutral", "Not analysed"]

filtered: list[tuple[int, dict]] = [
    (i, a)
    for i, a in enumerate(articles)
    if a["source"] in active_sources
    and _sentiment_bucket(i) in active_labels
]

if sort_by == "Date (newest)":
    filtered.sort(key=lambda x: x[1]["published"], reverse=True)
elif sort_by == "Date (oldest)":
    filtered.sort(key=lambda x: x[1]["published"])
elif sort_by == "Source A–Z":
    filtered.sort(key=lambda x: x[1]["source"])


# ══════════════════════════════════════════════════════════════════════════════
#  ARTICLE FEED  — two-column editorial grid
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Latest Dispatches</div>', unsafe_allow_html=True)

if not filtered:
    st.markdown(
        '<div class="no-results">No articles match the current filters.</div>',
        unsafe_allow_html=True,
    )
else:
    col_left, col_right = st.columns(2, gap="large")
    columns = [col_left, col_right]

    for pos, (article_idx, article) in enumerate(filtered):

        with columns[pos % 2]:

            # ── Static card HTML ───────────────────────────────────────────────
            pub_date = article["published"][:10]   # YYYY-MM-DD only
            snippet  = (
                _truncate(article["summary"], 200)
                or _truncate(article["text"], 200)
            )

            st.markdown(
                f"""
                <div class="article-card">
                    <div class="article-meta">
                        <span class="source-pill">{article['source']}</span>
                        {pub_date}
                    </div>
                    <div class="article-headline">{article['title']}</div>
                    <div class="article-snippet">{snippet}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Action row ─────────────────────────────────────────────────────
            action_col, link_col = st.columns([1, 1])

            with action_col:
                if article_idx in sentiments:
                    # Already scored — render the editorial badge
                    st.markdown(
                        _sentiment_tag_html(sentiments[article_idx]),
                        unsafe_allow_html=True,
                    )
                else:
                    # Not yet scored — show the editorial text button
                    if st.button("Check Sentiment", key=f"analyse_{article_idx}"):
                        with st.spinner("Scoring…"):
                            # ── Sole call into src.sentiment_model ─────────────
                            result = get_sentiment_scores(article["text"])
                        # Persist in session_state: scoring one article never
                        # affects the badges already shown on other articles
                        st.session_state.sentiments[article_idx] = result
                        st.rerun()

            with link_col:
                if article.get("link") and article["link"] not in ("#", ""):
                    st.markdown(
                        f'<a class="article-link" href="{article["link"]}" '
                        f'target="_blank" rel="noopener noreferrer">'
                        f'Read Full Article ↗</a>',
                        unsafe_allow_html=True,
                    )

            # Thin rule between cards within the same column
            st.markdown("<hr class='card-sep'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div style="
        text-align: center;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #777777;
        border-top: 1px solid #121212;
        margin-top: 3rem;
        padding-top: 1rem;
    ">
        The Sentiment Post · Powered by VADER NLP · Live RSS Data
    </div>
    """,
    unsafe_allow_html=True,
)