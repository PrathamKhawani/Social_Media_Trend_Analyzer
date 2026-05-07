import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from utils.data_updater import update_datasets
from utils.ui import set_premium_ui
from utils.model_trainer import main as retrain_models
from utils.trend_fetcher import get_niche_score, get_trending_now, level_color, level_emoji

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Social Media Trend Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GLOBAL CSS ─────────────────────────────────────────────────────────────────
set_premium_ui()


# ─── DATA LOADING ────────────────────────────────────────────────────────────────
@st.cache_data
def load_datasets():
    try:
        engagement = pd.read_csv(os.path.join(BASE_DIR, 'engagement.csv'))
    except Exception:
        engagement = None
    try:
        hashtags = pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'))
    except Exception:
        try:
            hashtags = pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'), encoding='latin1')
        except Exception:
            hashtags = None
    try:
        ts = pd.read_csv(os.path.join(BASE_DIR, 'time_series.csv'))
    except Exception:
        try:
            ts = pd.read_csv(os.path.join(BASE_DIR, 'time_series.csv'), encoding='latin1')
        except Exception:
            ts = None
    return engagement, hashtags, ts

engagement_df, hashtags_df, ts_df = load_datasets()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔄 Live Data")
    st.markdown("Keep your AI predictions accurate by fetching the latest social media trends.")
    if st.button("Fetch Live Trends", use_container_width=True, help="Click to simulate fetching the latest real-time social media data and automatically retrain AI models."):
        with st.status("🔄 Processing Live Data Update...", expanded=True) as status:
            st.write("📥 Fetching latest real-time datasets...")
            success, msg = update_datasets(100)
            if success:
                st.write("🧠 Retraining AI Models on new trends...")
                try:
                    retrain_models()
                    st.cache_data.clear()
                    status.update(label="✅ Data Updated & Models Retrained!", state="complete", expanded=False)
                    st.toast("Success: 100 new rows added and 4 AI models retrained!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during retraining: {e}")
            else:
                st.error(msg)

# ─── HERO HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <h1>
        Social Media Trend Analyzer
    </h1>
    <p>
        AI-powered dashboard to predict, analyze & forecast social media performance
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 Welcome! How to use this application?", expanded=True):
    st.markdown("""
    **Welcome to the Social Media Trend Analyzer!** This tool uses Artificial Intelligence to help you understand what's trending and how well your posts will perform.
    
    * **🔮 Trend Predictor:** Want to know if a hashtag will go viral? Type it here and our AI will tell you.
    * **📊 Post Analyzer:** Test your post idea before publishing. We'll score it and predict its reach.
    * **🔍 Hashtag Explorer:** Discover new hashtag groups related to your niche.
    * **📋 Data Explorer:** Dive into the raw social media data powering these insights.
    
    *Tip: Use the **Fetch Live Trends** button in the sidebar to inject the latest data!*
    """)

st.markdown("---")

# ─── LIVE MARKET PULSE ────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📡 Live Market Pulse — Real-Time Niche Scores</p>', unsafe_allow_html=True)
st.caption("📡 Powered by Google Trends · Auto-refreshes every hour")

niche_list = ["Technology", "Fitness", "Fashion", "Finance", "Gaming", "Food", "Travel", "Education"]
with st.spinner("Fetching live trend data…"):
    pulse_cols = st.columns(len(niche_list))
    for pcol, niche in zip(pulse_cols, niche_list):
        sc = get_niche_score(niche)
        lv = "Viral" if sc >= 75 else "High" if sc >= 50 else "Medium" if sc >= 25 else "Low"
        c  = level_color(lv)
        e  = level_emoji(lv)
        pcol.markdown(f"""
        <div style="background:var(--secondary-background-color);border:1px solid {c}44;
                    border-top:3px solid {c};border-radius:8px;padding:12px;text-align:center;">
            <div style="font-size:0.75rem;font-weight:600;opacity:0.7;">{niche}</div>
            <div style="font-size:1.5rem;font-weight:700;color:{c};margin:4px 0;">{e} {sc}</div>
            <div style="font-size:0.7rem;color:{c};">{lv}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── LIVE TRENDING NOW FEED ───────────────────────────────────────────────────────
st.markdown('<p class="section-header">🔥 Trending Now — Live from Google Trends</p>', unsafe_allow_html=True)
with st.spinner("Loading live trending topics…"):
    live_now = get_trending_now()
if live_now:
    t_cols = st.columns(5)
    for i, t in enumerate(live_now[:10]):
        with t_cols[i % 5]:
            st.markdown(f"""
            <div style="background:var(--secondary-background-color);border:1px solid rgba(255,107,53,0.3);
                        border-radius:8px;padding:12px;text-align:center;margin-bottom:8px;">
                <div style="font-size:0.85rem;font-weight:600;">{t['title']}</div>
                <div style="color:#ff6b35;font-size:0.8rem;margin-top:4px;">{t['traffic']}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── KPI METRICS ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Dataset Insights</p>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)


def kpi(col, icon, title, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

with k1:
    val  = f"{len(engagement_df):,}" if engagement_df is not None else "–"
    kpi(k1, "📝", "Instagram Posts", val, "engagement.csv")
with k2:
    val  = f"{len(hashtags_df):,}" if hashtags_df is not None else "–"
    kpi(k2, "#️⃣", "Hashtags Tracked", val, "hashtags.csv")
with k3:
    val  = f"{len(ts_df):,}" if ts_df is not None else "–"
    kpi(k3, "▶️", "YouTube Videos", val, "time_series.csv")
with k4:
    kpi(k4, "🧠", "ML Models Active", "4", "Trained & Ready")

st.markdown("<br>", unsafe_allow_html=True)

# ─── CHARTS ROW ──────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Dataset Insights</p>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

# Chart 1 – Engagement by media type
with c1:
    if engagement_df is not None:
        med = engagement_df.groupby('media_type')['engagement_rate'].mean().reset_index()
        fig = px.bar(
            med, x='media_type', y='engagement_rate',
            color='engagement_rate', color_continuous_scale='Blues',
            title="Avg Engagement Rate by Media Type",
            labels={'engagement_rate':'Avg Rate','media_type':'Media Type'}
        )
        fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# Chart 2 – Performance bucket distribution
with c2:
    if engagement_df is not None:
        bucket_counts = engagement_df['performance_bucket_label'].value_counts().reset_index()
        bucket_counts.columns = ['Bucket', 'Count']
        fig2 = px.pie(
            bucket_counts, names='Bucket', values='Count',
            title="Post Performance Distribution",
            hole=0.45,
            color_discrete_sequence=['#0070F3', '#333333', '#888888', '#555555']
        )
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

# ─── ROW 2 CHARTS ────────────────────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    if hashtags_df is not None:
        plat = hashtags_df.groupby('Platform')['Views'].mean().reset_index()
        fig3 = px.bar(
            plat, x='Platform', y='Views',
            color='Views', color_continuous_scale='Purples',
            title="Avg Views per Platform (Hashtags)"
        )
        fig3.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

with c4:
    if hashtags_df is not None:
        eng_lvl = hashtags_df['Engagement_Level'].value_counts().reset_index()
        eng_lvl.columns = ['Level','Count']
        fig4 = px.bar(
            eng_lvl, x='Level', y='Count',
            color='Count', color_continuous_scale='Greys',
            title="Hashtag Engagement Level Distribution"
        )
        fig4.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

# ─── AI FEATURES OVERVIEW ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-header">🧠 AI Features Overview</p>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="card">
        <h4 style="color:#0070F3;">🔮 Trend Predictor</h4>
        <p>Enter any hashtag + platform + region and get an instant AI prediction on whether it will achieve Low, Medium, High, or Viral engagement.</p>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="card">
        <h4 style="color:#0070F3;">📊 Post Analyzer</h4>
        <p>Simulate a post before publishing it. Our AI evaluates your content details and estimates your future engagement rate and performance level.</p>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="card">
        <h4 style="color:#0070F3;">🔍 Hashtag Explorer</h4>
        <p>Discover clusters of related trending hashtags. Our AI groups similar tags together on an interactive visual map to help you find new audiences.</p>
    </div>""", unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#3a4a5a; font-size:0.8rem; padding:0.5rem 0;">
    📈 Social Media Trend Analyzer · Data Science Semester Project · Built with Python, Scikit-Learn & Streamlit
</div>
""", unsafe_allow_html=True)
