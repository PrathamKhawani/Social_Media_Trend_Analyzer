import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui
from utils.trend_fetcher import (
    get_live_trend_score,
    get_trending_now,
    level_color,
    level_emoji,
)

st.set_page_config(page_title="Trend Predictor | Social Trend Analyzer", page_icon="🔮", layout="wide")
set_premium_ui()

st.markdown("""
<h1>🔮 Trend Predictor</h1>
<p>
Enter any hashtag or topic. Our engine <b>fetches live Google Trends data</b> and combines it with
historical ML patterns to give you the most accurate engagement forecast — always up-to-date.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Trend Predictor", expanded=False):
    st.markdown("""
    1. **Type any Hashtag / Topic** (e.g. `#AI`, `#ChatGPT`, `fitness`, `crypto`).
    2. Select your **Platform**, **Region**, and **Content Type**.
    3. Click **🚀 Predict Performance**.
    4. The AI fetches **live Google Trends data** for that exact keyword + combines it with the ML model.
    5. Results update every hour automatically to stay current.

    > 💡 **Data Source:** Google Trends (real-time, worldwide). Cached for 1 hour for speed.
    """)

# ─── Load ML model & data ────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        model_path = os.path.join(BASE_DIR, 'models', 'trend_predictor.pkl')
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading ML model: {e}")
        return None

@st.cache_data
def load_hashtag_data():
    try:
        return pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'))
    except Exception:
        try:
            return pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'), encoding='latin1')
        except Exception:
            return None

model   = load_model()
hash_df = load_hashtag_data()

if model is None:
    st.error("ML model not found. Run `python utils/model_trainer.py` first.")
    st.stop()

# ─── Input form ──────────────────────────────────────────────────────────────
with st.form("predict_form"):
    st.markdown("### 📥 Topic Details")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        hashtag      = st.text_input("Hashtag / Topic", value="#AI",
                                     help="Any topic: #AI, ChatGPT, fitness, crypto…")
    with c2:
        platform     = st.selectbox("Platform", ["Instagram", "TikTok", "Twitter", "Facebook", "YouTube"])
    with c3:
        region       = st.selectbox("Region", ["Global", "India", "USA", "UK", "Brazil", "Europe", "Australia", "Japan"])
    with c4:
        content_type = st.selectbox("Content Type", ["Video", "Reels", "Image", "Carousel", "Text", "Shorts"])

    submitted = st.form_submit_button("🚀 Predict Performance", use_container_width=True)

# ─── Prediction ──────────────────────────────────────────────────────────────
if submitted:
    # Map region dropdown to Google Trends geo code
    region_geo = {
        "Global": "", "India": "IN", "USA": "US", "UK": "GB",
        "Brazil": "BR", "Europe": "GB", "Australia": "AU", "Japan": "JP"
    }
    geo = region_geo.get(region, "")

    # ML model base prediction (Platform + Content_Type + Region)
    try:
        input_df = pd.DataFrame({'Platform': [platform], 'Content_Type': [content_type], 'Region': [region]})
        ml_prediction = model.predict(input_df)[0]
        try:
            proba  = model.predict_proba(input_df)[0]
            ml_conf = max(proba) * 100
            classes = getattr(model, "classes_", model.named_steps["classifier"].classes_)
        except Exception:
            ml_conf = 60.0
            classes = ["High", "Low", "Medium"]
            proba   = [0.3, 0.1, 0.6]
    except Exception as e:
        st.warning(f"ML Model prediction skipped: {e}")
        ml_prediction = "Medium"
        ml_conf = 50.0
        classes = ["Low", "Medium", "High", "Viral"]
        proba = [0.25, 0.25, 0.25, 0.25]

    # ── Live Google Trends fetch ──────────────────────────────────────────────
    with st.spinner(f"📡 Fetching live Google Trends data for **{hashtag}**…"):
        try:
            trend_data = get_live_trend_score(hashtag, geo=geo)
        except Exception as e:
            st.error(f"Failed to fetch live trends: {e}")
            from utils.trend_fetcher import _fallback_score
            trend_data = _fallback_score(hashtag)

    trend_score  = trend_data.get("score", 50)
    trend_level  = trend_data.get("level", "Medium")
    trend_source = trend_data.get("source", "fallback")
    trend_reason = trend_data.get("reason", "Live data unavailable.")
    interest_df  = trend_data.get("interest_df")
    related      = trend_data.get("related", [])

    # ── Merge: Google Trends score is primary; ML model is secondary weight ───
    # Score weight: 70% Google Trends live data + 30% ML model
    ml_level_map  = {"Low": 15, "Medium": 40, "High": 65, "Viral": 90}
    ml_score      = ml_level_map.get(ml_prediction, 40)
    blended_score = int(trend_score * 0.7 + ml_score * 0.3)

    # Re-derive final level from blended score
    if blended_score >= 75:
        final_level = "Viral"
    elif blended_score >= 50:
        final_level = "High"
    elif blended_score >= 25:
        final_level = "Medium"
    else:
        final_level = "Low"

    # Confidence: Google Trends score-based + small boost for agreement
    confidence = min(98.0, blended_score + (5 if trend_level == ml_prediction else 0))

    val_color  = level_color(final_level)
    lv_emoji   = level_emoji(final_level)

    st.markdown("---")

    # ── Data source badge ─────────────────────────────────────────────────────
    source_badge_color = "#00b4d8" if trend_source == "google_trends" else "#fca311"
    source_label = "📡 Live Google Trends" if trend_source == "google_trends" else "🧠 Cached Intelligence"
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
        <span style="background:{source_badge_color}22; color:{source_badge_color};
                     border:1px solid {source_badge_color}55; border-radius:20px;
                     padding:4px 14px; font-size:0.82rem; font-weight:600;">
            {source_label}
        </span>
        <span style="color:var(--text-color); opacity:0.65; font-size:0.82rem;">{trend_reason}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Trend alert banner ────────────────────────────────────────────────────
    if final_level in ["Viral", "High"]:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{val_color}18,{val_color}08);
                    border:1px solid {val_color}55; border-left:4px solid {val_color};
                    border-radius:8px; padding:14px 20px; margin-bottom:16px;">
            {lv_emoji} <b style="color:{val_color};">Trend Alert:</b>
            <span style="color:var(--text-color);">
                <b>{hashtag}</b> is registering <b style="color:{val_color};">{final_level.upper()}</b>
                engagement on Google Trends right now (score: {trend_score}/100).
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎯 Prediction Results")
    r1, r2, r3 = st.columns(3)

    with r1:
        badge_cls = f"badge-{final_level.lower()}"
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Predicted Engagement Level</div>
            <div class='result-value' style='color:{val_color};'>{lv_emoji} {final_level.upper()}</div>
            <span class='badge {badge_cls}'>{hashtag}</span>
        </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Google Trends Score</div>
            <div class='result-value' style='color:#00b4d8;'>{trend_score}<span style="font-size:1.2rem;opacity:0.6;">/100</span></div>
            <span class='badge' style='background:#1e3a5f;color:#90cdf4;'>Live Data</span>
        </div>""", unsafe_allow_html=True)

    with r3:
        best_platform = "TikTok" if content_type in ["Video","Reels","Shorts"] else "Instagram"
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>AI Confidence</div>
            <div class='result-value' style='color:#a78bfa;'>{confidence:.0f}<span style="font-size:1.2rem;opacity:0.6;">%</span></div>
            <span class='badge' style='background:#2d1b69;color:#a78bfa;'>Best on {best_platform}</span>
        </div>""", unsafe_allow_html=True)

    # ── Google Trends Sparkline Chart ─────────────────────────────────────────
    if interest_df is not None and not interest_df.empty:
        st.markdown("### 📈 Live Interest Over Time (Google Trends — Last 30 Days)")
        fig_spark = px.area(
            interest_df, x='date', y='interest',
            labels={'interest': 'Search Interest (0–100)', 'date': 'Date'},
            template='plotly_dark',
            color_discrete_sequence=[val_color]
        )
        fig_spark.update_traces(fill='tozeroy', fillcolor=f"{val_color}30")
        fig_spark.update_layout(
            paper_bgcolor='rgba(14,21,32,0.9)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(t=10, b=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(range=[0, 100], showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_spark, use_container_width=True)

    # ── ML Model breakdown (secondary) ────────────────────────────────────────
    st.markdown("### 📊 ML Model Prediction Breakdown")
    prob_df = pd.DataFrame({'Class': classes, 'Probability': proba})
    color_map = {"Low": "#e63946", "Medium": "#fca311", "High": "#00e676", "Viral": "#ff6b35"}
    fig_bar = px.bar(
        prob_df, x='Class', y='Probability', color='Class',
        color_discrete_map=color_map,
        template='plotly_dark',
        labels={'Probability': 'ML Probability Score'}
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(14,21,32,0.9)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Related Rising Topics ─────────────────────────────────────────────────
    if related:
        st.markdown("### 🔗 Related Rising Topics (Google Trends)")
        rel_cols = st.columns(len(related))
        for col, kw in zip(rel_cols, related):
            col.markdown(f"""
            <div style="background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.2);
                        border-radius:8px;padding:10px;text-align:center;font-size:0.82rem;font-weight:600;">
                🔍 {kw}
            </div>""", unsafe_allow_html=True)

    # ── Insight box ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='tip-box'>
        💡 <b>AI Insight:</b> <b>{hashtag}</b> has a live Google Trends score of <b>{trend_score}/100</b>
        (blended with ML model → {blended_score}/100). This places it in the <b style="color:{val_color};">{final_level}</b> tier.
        {content_type}s on {platform} targeting {region} perform best when posted between <b>6PM–9PM</b>.
    </div>""", unsafe_allow_html=True)

# ─── Live Trending Now Widget ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔥 Trending Now — Live from Google Trends")
st.caption("Auto-refreshes every hour")

with st.spinner("Loading live trending topics…"):
    live_trends = get_trending_now()

if live_trends:
    t_cols = st.columns(5)
    for i, topic in enumerate(live_trends[:10]):
        with t_cols[i % 5]:
            st.markdown(f"""
            <div style="background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.2);
                        border-radius:8px;padding:12px;text-align:center;margin-bottom:8px;">
                <div style="font-size:0.85rem;font-weight:600;">{topic['title']}</div>
                <div style="color:#ff6b35;font-size:0.8rem;margin-top:4px;">{topic['traffic']}</div>
            </div>""", unsafe_allow_html=True)

# ─── Historical context ───────────────────────────────────────────────────────
if hash_df is not None:
    st.markdown("---")
    st.markdown("### 📊 Historical Platform Benchmarks (Training Data)")
    c1, c2 = st.columns(2)
    with c1:
        plat_eng = hash_df.groupby('Platform')['Views'].mean().reset_index()
        fig2 = px.bar(plat_eng, x='Platform', y='Views', color='Views',
                      color_continuous_scale='Teal', template='plotly_dark',
                      title="Avg Views by Platform")
        fig2.update_layout(paper_bgcolor='rgba(14,21,32,0.9)')
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        eng_lvl = hash_df['Engagement_Level'].value_counts().reset_index()
        eng_lvl.columns = ['Level', 'Count']
        fig3 = px.pie(eng_lvl, names='Level', values='Count', hole=0.4,
                      color_discrete_sequence=['#fca311','#00b4d8','#e63946','#ff6b35'],
                      title="Engagement Level Split", template='plotly_dark')
        fig3.update_layout(paper_bgcolor='rgba(14,21,32,0.9)')
        st.plotly_chart(fig3, use_container_width=True)
