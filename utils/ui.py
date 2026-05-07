import streamlit as st

def set_premium_ui():
    """Injects Vercel/Linear inspired hyper-premium minimalist dark mode CSS."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Font & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-color);
    }
    
    /* Typography Overrides */
    h1 {
        color: var(--text-color) !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em !important;
    }
    h2, h3, h4 {
        color: var(--text-color) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    p {
        color: var(--text-color) !important;
        opacity: 0.8 !important;
        line-height: 1.6 !important;
    }
    
    /* Premium KPI Cards & Containers */
    .kpi-card, .result-card, .preview-box, .card, .comment-card {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 8px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .kpi-card:hover, .result-card:hover, .card:hover {
        border-color: var(--primary-color) !important;
    }
    
    /* Metric Typography within Cards */
    .kpi-title, .result-label, .card-title {
        color: var(--text-color) !important;
        opacity: 0.7 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 600 !important;
    }
    .kpi-value, .result-value, .card-value {
        color: var(--text-color) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        margin: 8px 0 !important;
    }
    
    /* Subtle Accents (Buttons, Info boxes) */
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        transition: transform 0.2s ease, opacity 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        border-color: var(--primary-color) !important;
    }
    
    /* Tip box / Alerts */
    .tip-box {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-left: 4px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 16px !important;
        color: var(--text-color) !important;
    }
    </style>
    """, unsafe_allow_html=True)
