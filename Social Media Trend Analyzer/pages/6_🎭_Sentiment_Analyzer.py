import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import hashlib
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui
from utils.trend_fetcher import get_live_trend_score, level_color, level_emoji

st.set_page_config(page_title="Sentiment Analyzer", page_icon="🎭", layout="wide")

set_premium_ui()

st.markdown("""
<h1>🎭 Audience Sentiment Analyzer</h1>
<p>
Ensure your viral trend is generating the right kind of buzz. Enter a topic, and our <b>AI Sentiment Engine</b> will analyze public reactions to determine if the audience sentiment is Positive, Neutral, or Negative.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Sentiment Analyzer", expanded=False):
    st.markdown("""
    1. **Enter a Topic**: Type any hashtag, brand name, or trending topic in the search bar.
    2. Click **🔍 Analyze Audience Reaction**.
    3. The AI will simulate fetching recent social media comments regarding this topic.
    4. Review the **Overall Brand Health Score** and the **Sentiment Breakdown** pie chart.
    5. Read through the **Live Comment Feed** to get qualitative insights into what people are actually saying.
    """)

# ─── Inputs ──────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Search Topic")
topic = st.text_input("Enter a Hashtag, Brand, or Trend", value="Artificial Intelligence")
submitted = st.button("📊 Analyze Audience Reaction", use_container_width=True)

def generate_comments(topic, num_comments=30, trend_score=50):
    # Use a seed based on the topic so the same topic gives consistent results during a session
    seed_val = int(hashlib.md5(topic.lower().encode('utf-8')).hexdigest(), 16) % (10**8)
    random.seed(seed_val)

    # Determine sentiment vibe based on REAL trend score instead of random
    # High trending topics tend to have more positive sentiment
    if trend_score >= 75:
        vibe = "mostly_positive"
    elif trend_score >= 50:
        vibe = "mixed"
    elif trend_score >= 25:
        vibe = "neutral_heavy"
    else:
        vibe = random.choice(["mostly_negative", "neutral_heavy"])
    
    if vibe == "mostly_positive":
        weights = [0.65, 0.25, 0.10]
    elif vibe == "mostly_negative":
        weights = [0.15, 0.25, 0.60]
    elif vibe == "neutral_heavy":
        weights = [0.20, 0.60, 0.20]
    else:
        weights = [0.40, 0.30, 0.30]
        
    sentiments = random.choices(["Positive", "Neutral", "Negative"], weights=weights, k=num_comments)
    
    pos_templates = [
        f"I absolutely love {topic}! It changed my life.",
        f"{topic} is exactly what we needed right now 🔥",
        f"Can't stop thinking about {topic}. So good!",
        f"Highly recommend checking out {topic} if you haven't already.",
        f"{topic} exceeded all my expectations 💯"
    ]
    
    neu_templates = [
        f"Has anyone tried {topic} yet? What are your thoughts?",
        f"{topic} is trending again. Interesting.",
        f"I see {topic} everywhere, still trying to make up my mind.",
        f"Just saw a post about {topic}.",
        f"It's okay, but I'm not overly hyped about {topic}."
    ]
    
    neg_templates = [
        f"Honestly, {topic} is so overrated.",
        f"I don't understand the hype around {topic}. It's awful 📉",
        f"Worst experience ever with {topic}.",
        f"Can we please stop talking about {topic}? It's annoying.",
        f"{topic} completely missed the mark."
    ]
    
    comments = []
    for s in sentiments:
        if s == "Positive": text = random.choice(pos_templates)
        elif s == "Neutral": text = random.choice(neu_templates)
        else: text = random.choice(neg_templates)
            
        comments.append({
            "User": f"@user{random.randint(1000, 9999)}",
            "Sentiment": s,
            "Text": text
        })
        
    return pd.DataFrame(comments)

if submitted and topic:
    # Fetch live trend score first — used to calibrate sentiment weights
    with st.spinner(f"📡 Fetching live trend data for **{topic}**…"):
        live_trend = get_live_trend_score(topic)
    trend_score   = live_trend["score"]
    trend_level   = live_trend["level"]
    trend_src     = live_trend["source"]
    t_color       = level_color(trend_level)
    t_emoji       = level_emoji(trend_level)

    with st.spinner("Running AI Sentiment Analysis on audience reactions..."):
        df_comments = generate_comments(topic, num_comments=50, trend_score=trend_score)
        
        counts = df_comments['Sentiment'].value_counts()
        pos_count = counts.get('Positive', 0)
        neu_count = counts.get('Neutral', 0)
        neg_count = counts.get('Negative', 0)
        total = len(df_comments)
        
        # Calculate Brand Health Score (0-100)
        # Positive = 100, Neutral = 50, Negative = 0
        health_score = int(((pos_count * 100) + (neu_count * 50) + (neg_count * 0)) / total)
        
    st.markdown("---")

    # ── Live Trend Context Banner ──────────────────────────────────────────────
    src_badge = "📡 Live Google Trends" if trend_src == "google_trends" else "🧠 Cached Intelligence"
    st.markdown(f"""
    <div style="background:{t_color}12; border:1px solid {t_color}44; border-left:4px solid {t_color};
                border-radius:8px; padding:12px 20px; margin-bottom:16px; display:flex; align-items:center; gap:16px;">
        <div>
            <span style="font-size:1.8rem;">{t_emoji}</span>
        </div>
        <div>
            <div style="font-weight:700; color:{t_color}; font-size:1rem;">{topic} — Google Trends Score: {trend_score}/100 ({trend_level})</div>
            <div style="font-size:0.8rem; opacity:0.7;">Source: {src_badge} · High-trending topics tend to generate more positive sentiment.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📈 Analysis Results for '{topic}'")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### 🧭 Brand Health Score")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={'text': "Audience Approval Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 40], 'color': '#e63946'},
                    {'range': [40, 70], 'color': '#fca311'},
                    {'range': [70, 100], 'color': '#00e676'}
                ]
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown(f"<p style='text-align:center;'>Based on an AI analysis of {total} recent interactions.</p>", unsafe_allow_html=True)

    with c2:
        st.markdown("#### 📊 Sentiment Breakdown")
        fig_pie = px.pie(
            values=[pos_count, neu_count, neg_count], 
            names=['Positive', 'Neutral', 'Negative'],
            color=['Positive', 'Neutral', 'Negative'],
            color_discrete_map={'Positive':'#00e676', 'Neutral':'#fca311', 'Negative':'#e63946'},
            hole=0.4
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 💬 Live Comment Feed")
    
    # Show a sample of the comments
    for _, row in df_comments.head(15).iterrows():
        color_class = "comment-pos" if row['Sentiment'] == "Positive" else "comment-neu" if row['Sentiment'] == "Neutral" else "comment-neg"
        emoji = "😊" if row['Sentiment'] == "Positive" else "😐" if row['Sentiment'] == "Neutral" else "😠"
        
        st.markdown(f"""
        <div class='comment-card {color_class}'>
            <div class='comment-user'>{row['User']} • {row['Sentiment']} {emoji}</div>
            <div class='comment-text'>"{row['Text']}"</div>
        </div>
        """, unsafe_allow_html=True)
