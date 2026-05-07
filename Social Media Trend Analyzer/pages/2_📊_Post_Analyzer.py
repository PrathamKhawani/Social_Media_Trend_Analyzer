import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui

st.set_page_config(page_title="Post Analyzer | Social Trend Analyzer", page_icon="📊", layout="wide")

set_premium_ui()

st.markdown("""
<h1>📊 Post Analyzer & Engagement Forecaster</h1>
<p>
Simulate a post before you publish it. Our <b>AI Analyzer</b> evaluates your configuration to predict your performance category and forecast your expected engagement rate.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Post Analyzer", expanded=False):
    st.markdown("""
    1. **Fill out your post details** such as follower count, media type, and caption length.
    2. Click **🚀 Analyze Post** to run the simulation.
    3. Review the **Performance Bucket**, **Expected Engagement Rate**, and **Estimated Reach**.
    4. Check the **Best Hours to Post** chart to optimize your posting time!
    """)

@st.cache_resource
def load_models():
    try:
        clf_path = os.path.join(BASE_DIR, 'models', 'performance_classifier.pkl')
        reg_path = os.path.join(BASE_DIR, 'models', 'engagement_regressor.pkl')
        clf = joblib.load(clf_path)
        reg = joblib.load(reg_path)
        return clf, reg
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

classifier, regressor = load_models()

if classifier is None:
    st.error("Models not found. Run `python utils/model_trainer.py` first.")
    st.stop()

import random

def generate_captions(category, media, cta):
    hooks = {
        "Technology": ["Is this the end of smartphones? 📱", "I tested the top 3 gadgets so you don't have to.", "The hidden feature Apple didn't tell you about 🤫"],
        "Fitness": ["Stop doing your squats like this! 🛑", "3 exercises for a bulletproof core.", "My entire morning routine revealed. ☕"],
        "Beauty": ["The $5 drugstore find that beats luxury brands.", "My secret to glowing skin in 5 minutes.", "GRWM: The ultimate night out look ✨"],
        "Finance": ["How I saved $10k in 6 months without trying.", "The biggest money mistake you're making right now.", "Index funds vs Real Estate: The truth 📈"],
        "Food": ["The only pasta recipe you'll ever need 🍝", "I tried the viral TikTok recipe so you don't have to.", "3-ingredient dessert that takes 5 minutes!"],
        "Travel": ["The most underrated city in Europe ✈️", "How to pack for 2 weeks in one carry-on.", "My honest review of the Maldives 🏝️"],
        "Gaming": ["The best loadout for Season 5 🎮", "How I beat the hardest boss in under 2 minutes.", "This hidden easter egg changes everything!"],
        "Education": ["The study hack that got me a 4.0 GPA 📚", "Stop studying harder, start studying smarter.", "5 websites every student needs to know."],
        "Fashion": ["3 ways to style a basic white tee 👕", "Trend alert: What's in for Fall 2026.", "My honest review of the viral Zara jacket."],
        "Entertainment": ["You won't believe what happened at the end 😱", "My top 5 favorite movies of all time 🍿", "The truth behind the latest drama..."]
    }
    default_hooks = ["Wait until the end for this... 👀", "I can't believe I'm sharing my secret 🤫", "This changes everything!"]
    
    bodies = [
        "I've been experimenting with this for the past few weeks and the results are mind-blowing. If you want to achieve similar results, you need to be consistent and pay attention to the details. Save this post so you don't forget it!",
        "It took me years of trial and error to finally figure this out. I wish I knew this when I first started! The key is to keep it simple and focus on what actually moves the needle.",
        "A lot of people asked me about this, so here is the complete breakdown! Make sure you watch carefully because I dropped a lot of gems in this one.",
        "Here is the exact strategy I use every single day. It's not always easy, but it is definitely worth it. Double tap if you agree!"
    ]
    ctas = [
        "👇 Let me know what you think in the comments!",
        "💾 Save this for later so you don't lose it!",
        "🚀 Tag a friend who needs to see this!",
        "🔗 Click the link in my bio for the full guide!",
        "✅ Follow me for more tips like this every day!"
    ]
    
    cat_hooks = hooks.get(category, default_hooks).copy()
    random.shuffle(cat_hooks)
    
    opt1 = f"{cat_hooks[0]}\\n\\n" + ("" if media == "text" else f"Watch the {media} to see exactly how it works. ") + f"Have you ever tried this? Drop a comment below! 👇"
    
    b_idx = random.randint(0, len(bodies)-1)
    c_idx = random.randint(0, len(ctas)-1)
    opt2 = f"{cat_hooks[1]}\\n\\n{bodies[b_idx]}\\n\\n" + (ctas[c_idx] if cta else "Thanks for watching/reading!")
    
    opt3 = f"{cat_hooks[2]} 🔥\\n\\n#trending #{category.lower().replace(' ', '')} #viral"
    
    return opt1, opt2, opt3

# ─── Input Form ──────────────────────────────────────────────────────────────
with st.form("post_form"):
    st.markdown("### 📝 Configure Your Post")
    c1, c2, c3 = st.columns(3)

    with c1:
        follower_count = st.number_input("Follower Count", 0, 10_000_000, 15_000, step=1000)
        media_type     = st.selectbox("Media Type", ["reel", "image", "video", "carousel", "text"])
        caption_length = st.slider("Caption Length (chars)", 0, 2200, 150)

    with c2:
        content_cat    = st.selectbox("Content Category", ["Technology","Fitness","Beauty","Fashion","Gaming","Education","Food","Travel","Finance","Entertainment"])
        post_hour      = st.slider("Post Hour (24h)", 0, 23, 18)
        hashtags_count = st.slider("Number of Hashtags", 0, 30, 5)

    with c3:
        day_of_week    = st.selectbox("Day of Week", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        has_cta_r      = st.radio("Has Call to Action?", ["Yes","No"])

    submitted = st.form_submit_button("🚀 Analyze Post", use_container_width=True)

if submitted:
    has_cta = 1 if has_cta_r == "Yes" else 0
    input_df = pd.DataFrame({
        'follower_count':    [follower_count],
        'media_type':        [media_type],
        'content_category':  [content_cat],
        'post_hour':         [post_hour],
        'day_of_week':       [day_of_week],
        'hashtags_count':    [hashtags_count],
        'caption_length':    [caption_length],
        'has_call_to_action':[has_cta]
    })

    with st.spinner("AI is analyzing thousands of past posts to forecast yours…"):
        try:
            bucket  = classifier.predict(input_df)[0]
            eng_rate = max(0, float(regressor.predict(input_df)[0]))
        except Exception as e:
            st.error("ML Prediction Failed!")
            st.exception(e)
            st.stop()

    bucket_color = {
        'viral':  '#9b59b6', 'high': '#00e676',
        'medium': '#fca311', 'low':  '#e63946'
    }.get(bucket.lower(), '#fca311')

    st.markdown("---")
    st.markdown("### 🎯 Prediction Results")
    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Performance Bucket</div>
            <div class='result-value' style='color:{bucket_color};'>{bucket.upper()}</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Predicted Engagement Rate</div>
            <div class='result-value' style='color:#00b4d8;'>{eng_rate:.3f}%</div>
        </div>""", unsafe_allow_html=True)
    with r3:
        reach_est = int(follower_count * eng_rate * 3.5)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Estimated Reach</div>
            <div class='result-value' style='color:#a78bfa;'>{reach_est:,}</div>
        </div>""", unsafe_allow_html=True)

    # ─── Gauge chart for engagement rate ─────────────────────────────────────
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=eng_rate * 100,
        title={'text': "Engagement Rate Score"},
        delta={'reference': 5.0, 'increasing': {'color': '#00e676'}, 'decreasing': {'color': '#e63946'}},
        gauge={
            'axis':  {'range': [0, 20]},
            'bar':   {'color': bucket_color},
            'bgcolor': '#1a1f35',
            'steps': [
                {'range': [0,  3],  'color': '#1a1f1f'},
                {'range': [3,  8],  'color': '#1a2a1a'},
                {'range': [8,  20], 'color': '#1a2a2a'}
            ],
            'threshold': {'line': {'color': '#fca311', 'width': 3}, 'thickness': 0.75, 'value': eng_rate * 100}
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ─── Best hour recommendation ─────────────────────────────────────────────
    st.markdown("### ⏰ Best Hours to Post (Historical Avg Engagement)")
    try:
        eng_df = pd.read_csv(os.path.join(BASE_DIR, 'engagement.csv'))
        hour_rate = eng_df.groupby('post_hour')['engagement_rate'].mean().reset_index()
        fig_hour = px.bar(hour_rate, x='post_hour', y='engagement_rate',
                          color='engagement_rate', color_continuous_scale='Oranges',
                          labels={'post_hour':'Hour of Day','engagement_rate':'Avg Engagement Rate'},
                          title="Avg Engagement Rate by Posting Hour")
        fig_hour.add_vline(x=post_hour, line_color='#00e676', line_dash='dash',
                           annotation_text=f"Your hour ({post_hour}:00)", annotation_font_color='#00e676')
        fig_hour.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hour, use_container_width=True)
    except Exception:
        pass

    best_hours = "6PM – 9PM" if media_type in ["reel","video"] else "8AM – 11AM"
    st.markdown(f"""
    <div class='tip-box'>
        💡 <b>Pro Tip:</b> {media_type.capitalize()}s perform best between <b>{best_hours}</b>.
        Adding a clear Call-to-Action can increase engagement by up to <b>23%</b>.
        Aim for <b>{hashtags_count + 3} – {hashtags_count + 7}</b> hashtags for optimal reach.
    </div>""", unsafe_allow_html=True)

    # ─── AI Viral Caption Generator ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✍️ AI Viral Caption & Hook Generator")
    st.markdown(f"<p>Based on your {content_cat} {media_type}, our AI has crafted 3 ready-to-use captions to maximize your engagement.</p>", unsafe_allow_html=True)
    
    with st.spinner("Generating viral hooks and captions..."):
        cap1, cap2, cap3 = generate_captions(content_cat, media_type, has_cta)
    
    c_gen1, c_gen2, c_gen3 = st.columns(3)
    
    with c_gen1:
        st.markdown("**Option 1: Engagement Bait**")
        st.info(cap1)
        st.button("📋 Copy Option 1", key="copy1", help="Highlight text to copy")
        
    with c_gen2:
        st.markdown("**Option 2: The Storyteller**")
        st.success(cap2)
        st.button("📋 Copy Option 2", key="copy2", help="Highlight text to copy")
        
    with c_gen3:
        st.markdown("**Option 3: Short & Punchy**")
        st.warning(cap3)
        st.button("📋 Copy Option 3", key="copy3", help="Highlight text to copy")

