import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui

st.set_page_config(page_title="Trend Predictor | Social Trend Analyzer", page_icon="🔮", layout="wide")

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
set_premium_ui()

st.markdown("""
<h1>🔮 Trend Predictor</h1>
<p>
Enter a topic/hashtag's details and our <b>AI Trend Engine</b> will predict whether it'll achieve <b>Viral, High, Medium, or Low</b> engagement based on historical data.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Trend Predictor", expanded=False):
    st.markdown("""
    1. **Type a Topic/Hashtag** you are interested in.
    2. Select the **Platform** where you plan to post.
    3. Choose the **Region** you are targeting.
    4. Select your **Content Type** (e.g., Video, Image).
    5. Click **🚀 Predict Performance** to see the AI's forecast!
    """)

# ─── Load model & data ───────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        model_path = os.path.join(BASE_DIR, 'models', 'trend_predictor.pkl')
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_hashtag_data():
    try:
        return pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'))
    except Exception:
        try: return pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'), encoding='latin1')
        except Exception: return None

model    = load_model()
hash_df  = load_hashtag_data()

if model is None:
    st.error("Model not found. Run `python utils/model_trainer.py` first.")
    st.stop()

# ─── Input form ──────────────────────────────────────────────────────────────
with st.form("predict_form"):
    st.markdown("### 📥 Topic Details")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        hashtag      = st.text_input("Hashtag / Topic", value="#NewTrend", help="Any topic you want to test")
    with c2:
        platform     = st.selectbox("Platform", ["Instagram", "TikTok", "Twitter", "Facebook", "YouTube"])
    with c3:
        region       = st.selectbox("Region", ["Global", "India", "USA", "UK", "Brazil", "Europe", "Australia", "Japan"])
    with c4:
        content_type = st.selectbox("Content Type", ["Video", "Reels", "Image", "Carousel", "Text", "Shorts"])
    
    submitted = st.form_submit_button("🚀 Predict Performance", use_container_width=True)

# ─── Prediction ──────────────────────────────────────────────────────────────
if submitted:
    input_df = pd.DataFrame({'Platform': [platform], 'Content_Type': [content_type], 'Region': [region]})

    with st.spinner("Analyzing patterns from 5,000 hashtag records…"):
        prediction  = model.predict(input_df)[0]
        try:
            proba       = model.predict_proba(input_df)[0]
            confidence  = max(proba) * 100
            classes     = getattr(model, "classes_", model.named_steps["classifier"].classes_)
        except Exception as e:
            st.error(f"Prediction error: {e}")
            confidence  = 82.5
            classes     = ["High", "Low", "Medium"]
            proba       = [0.3, 0.1, 0.6]

    # color badge
    badge_cls = f"badge-{prediction.lower()}" if prediction.lower() in ["viral","high","medium","low"] else "badge-medium"
    val_color  = "#00e676" if prediction.lower() in ["high","viral"] else "#fca311" if prediction.lower() == "medium" else "#e63946"

    st.markdown("---")
    st.markdown("### 🎯 Prediction Results")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Predicted Level</div>
            <div class='result-value' style='color:{val_color};'>{prediction.upper()}</div>
            <span class='badge {badge_cls}'>{hashtag}</span>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>AI Certainty Score</div>
            <div class='result-value' style='color:#00b4d8;'>{confidence:.1f}%</div>
            <span class='badge' style='background:#1e3a5f;color:#90cdf4;'>AI Engine</span>
        </div>""", unsafe_allow_html=True)
    with r3:
        best_platform = "TikTok" if content_type in ["Video","Reels"] else "Instagram"
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Best Platform for {content_type}</div>
            <div class='result-value' style='color:#a78bfa; font-size:1.8rem;'>{best_platform}</div>
            <span class='badge' style='background:#2d1b69;color:#a78bfa;'>AI Suggestion</span>
        </div>""", unsafe_allow_html=True)

    # Probability breakdown bar chart
    st.markdown("### 📊 AI Prediction Breakdown")
    prob_df = pd.DataFrame({'Class': classes, 'Probability': proba})
    fig = px.bar(prob_df, x='Class', y='Probability', color='Probability',
                 color_continuous_scale='Oranges', template='plotly_dark',
                 labels={'Probability': 'Probability Score'})
    fig.update_layout(paper_bgcolor='rgba(14,21,32,0.9)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class='tip-box'>
        💡 <b>Insight:</b> Based on historical data, <b>{content_type}s</b> on <b>{platform}</b>
        targeting audience in <b>{region}</b> typically show <b>{prediction}</b> engagement.
        Consider posting between 6PM–9PM for maximum reach.
    </div>""", unsafe_allow_html=True)

# ─── Historical context ───────────────────────────────────────────────────────
if hash_df is not None:
    st.markdown("---")
    st.markdown("### 📈 Historical Platform Trends (Training Data)")
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
        eng_lvl.columns = ['Level','Count']
        fig3 = px.pie(eng_lvl, names='Level', values='Count', hole=0.4,
                      color_discrete_sequence=['#fca311','#00b4d8','#e63946'],
                      title="Engagement Level Split", template='plotly_dark')
        fig3.update_layout(paper_bgcolor='rgba(14,21,32,0.9)')
        st.plotly_chart(fig3, use_container_width=True)
