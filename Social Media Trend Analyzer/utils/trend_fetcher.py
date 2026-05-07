"""
utils/trend_fetcher.py
─────────────────────────────────────────────────────────────────────────────
Live Trend Intelligence Engine — powered by Google Trends (pytrends).
Provides real-time interest scores, trending topics, and related keywords.
All results are cached for 1 hour to prevent rate-limiting.
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import pandas as pd
import time
import re

# ─── Last-resort keyword fallback (only used if Google Trends is unavailable) ─
# Maps cleaned keyword fragments → guaranteed engagement level
_FALLBACK_SCORES = {
    # Viral tier
    "ai": 95, "artificialintelligence": 95, "chatgpt": 96, "gpt": 93,
    "openai": 92, "gemini": 90, "deepseek": 89, "copilot": 88, "llm": 87,
    "sora": 86, "agi": 85, "claude": 84,
    # High tier
    "machinelearning": 72, "deeplearning": 71, "datascience": 70,
    "python": 68, "coding": 67, "programming": 66, "tech": 65,
    "technology": 64, "startup": 63, "innovation": 62, "automation": 61,
    "cybersecurity": 60, "crypto": 59, "bitcoin": 62, "ethereum": 58,
    "fitness": 65, "gym": 63, "workout": 61, "health": 64, "wellness": 60,
    "reels": 68, "viral": 70, "trending": 69, "fyp": 72, "foryou": 71,
    "gaming": 64, "esports": 62, "music": 63, "fashion": 61, "ootd": 60,
    "travel": 58, "photography": 57, "investing": 59, "stocks": 58,
    # Medium tier
    "food": 48, "recipe": 46, "cooking": 45, "education": 44, "books": 42,
    "nature": 40, "sports": 49, "art": 43, "design": 44, "yoga": 41,
    "meditation": 40, "business": 48, "marketing": 47, "branding": 43,
}


def _normalize_keyword(keyword: str) -> str:
    """Strip # and spaces, lowercase — used for fallback matching."""
    return re.sub(r'[^a-z0-9]', '', keyword.lower())


def _score_to_level(score: float) -> str:
    """Convert a 0–100 interest score to an engagement level label."""
    if score >= 75:
        return "Viral"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"


def _fallback_score(keyword: str) -> dict:
    """
    Last-resort scoring when Google Trends is unavailable.
    Uses substring matching against known keywords.
    """
    norm = _normalize_keyword(keyword)
    best_score = 20  # default Low
    for kw, score in _FALLBACK_SCORES.items():
        if kw in norm:
            best_score = max(best_score, score)
    level = _score_to_level(best_score)
    return {
        "score": best_score,
        "level": level,
        "source": "fallback",
        "interest_df": None,
        "related": [],
        "reason": f"Google Trends unavailable — using cached intelligence. Score: {best_score}/100"
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_live_trend_score(keyword: str, timeframe: str = "today 1-m", geo: str = "") -> dict:
    """
    Fetch live Google Trends interest score for a keyword.

    Parameters
    ----------
    keyword  : The hashtag/topic to analyze (e.g. "#AI", "ChatGPT")
    timeframe: pytrends timeframe string. Default = last 30 days.
    geo      : Country code (e.g. "US", "IN"). Empty = worldwide.

    Returns
    -------
    dict with keys:
        score        - int 0–100 (avg interest over the period)
        level        - "Viral" | "High" | "Medium" | "Low"
        peak         - int (max score in the period)
        interest_df  - pd.DataFrame with date & interest columns (for sparkline)
        related      - list of related rising query strings
        source       - "google_trends" | "fallback"
        reason       - human-readable explanation
    """
    # Clean keyword for Google Trends (remove # prefix)
    clean_kw = keyword.strip().lstrip('#').strip()
    if not clean_kw:
        return _fallback_score(keyword)

    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=330, timeout=(10, 25), retries=2, backoff_factor=0.5)
        pytrends.build_payload([clean_kw], cat=0, timeframe=timeframe, geo=geo, gprop='')

        interest_df = pytrends.interest_over_time()

        if interest_df.empty or clean_kw not in interest_df.columns:
            return _fallback_score(keyword)

        series = interest_df[clean_kw]
        avg_score = int(series.mean())
        peak_score = int(series.max())

        # Fetch related queries for "rising" keywords
        try:
            related_data = pytrends.related_queries()
            rising = related_data.get(clean_kw, {}).get('rising')
            if rising is not None and not rising.empty and 'query' in rising.columns:
                related_list = rising['query'].head(5).tolist()
            else:
                related_list = []
        except Exception:
            related_list = []

        level = _score_to_level(avg_score)

        # Build clean interest df for sparkline
        chart_df = interest_df[[clean_kw]].reset_index()
        chart_df.columns = ['date', 'interest']

        return {
            "score": avg_score,
            "peak": peak_score,
            "level": level,
            "interest_df": chart_df,
            "related": related_list,
            "source": "google_trends",
            "reason": (
                f"Google Trends data (last 30 days). "
                f"Average interest: {avg_score}/100 — Peak: {peak_score}/100."
            )
        }

    except ImportError:
        # pytrends not installed
        return _fallback_score(keyword)
    except Exception:
        # Rate limit or network error → graceful fallback
        return _fallback_score(keyword)


@st.cache_data(ttl=3600, show_spinner=False)
def get_trending_now(geo: str = "") -> list[dict]:
    """
    Fetch today's top trending searches from Google Trends.

    Returns a list of dicts: [{"title": "...", "traffic": "..."}, ...]
    Falls back to a hardcoded list if unavailable.
    """
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=330, timeout=(10, 25), retries=2, backoff_factor=0.5)
        trending_df = pytrends.trending_searches(pn='united_states')
        topics = []
        for title in trending_df[0].head(10).tolist():
            topics.append({"title": title, "traffic": "🔥 Trending"})
        return topics if topics else _fallback_trending()
    except Exception:
        return _fallback_trending()


def _fallback_trending() -> list[dict]:
    """Hardcoded trending topics as last resort — updated periodically."""
    return [
        {"title": "AI", "traffic": "🔥 Viral"},
        {"title": "ChatGPT", "traffic": "🔥 Viral"},
        {"title": "Machine Learning", "traffic": "📈 High"},
        {"title": "Tech 2026", "traffic": "📈 High"},
        {"title": "Fitness", "traffic": "📈 High"},
        {"title": "Crypto", "traffic": "📈 High"},
        {"title": "Gaming", "traffic": "📈 High"},
        {"title": "Fashion", "traffic": "📊 Medium"},
        {"title": "Travel", "traffic": "📊 Medium"},
        {"title": "Food", "traffic": "📊 Medium"},
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def compare_keywords(keywords: list[str], geo: str = "") -> pd.DataFrame:
    """
    Compare up to 5 keywords side-by-side using Google Trends.
    Returns a DataFrame with columns = keywords and rows = dates.
    Used in Competitor Benchmarking for niche comparison.
    """
    if not keywords:
        return pd.DataFrame()
    keywords = [k.lstrip('#').strip() for k in keywords[:5]]  # max 5 for pytrends
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=330, timeout=(10, 25), retries=2, backoff_factor=0.5)
        pytrends.build_payload(keywords, timeframe='today 3-m', geo=geo)
        df = pytrends.interest_over_time()
        if 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
        return df
    except Exception:
        return pd.DataFrame()


def get_niche_score(niche: str) -> int:
    """
    Get a live interest score for a broad niche/category.
    Maps niche names to representative search terms then fetches from Google Trends.
    """
    niche_map = {
        "Technology": "technology",
        "Fitness":    "fitness",
        "Beauty":     "beauty",
        "Finance":    "investing",
        "Food":       "food recipes",
        "Travel":     "travel",
        "Gaming":     "gaming",
        "Fashion":    "fashion",
        "Education":  "online learning",
        "Entertainment": "entertainment",
    }
    search_term = niche_map.get(niche, niche.lower())
    result = get_live_trend_score(search_term)
    return result.get("score", 50)


def level_color(level: str) -> str:
    """Return the brand color for a given engagement level."""
    return {
        "Viral":  "#ff6b35",
        "High":   "#00e676",
        "Medium": "#fca311",
        "Low":    "#e63946",
    }.get(level, "#fca311")


def level_emoji(level: str) -> str:
    """Return an emoji for a given engagement level."""
    return {
        "Viral":  "🔥",
        "High":   "📈",
        "Medium": "📊",
        "Low":    "📉",
    }.get(level, "📊")
