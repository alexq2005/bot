import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from src.config import settings

# Page Config
st.set_page_config(page_title="IOL Evolutionary Bot", layout="wide", page_icon="🧬")

# Database Connection
@st.cache_resource
def get_engine():
    return create_engine(settings.DB_URL)

engine = get_engine()

# --- HEADER ---
st.title("🧬 IOL Evolutionary Trading Bot (SOTA v2.0)")
st.markdown("### Self-Improving AI for the Argentine Market")

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        trades_count = pd.read_sql("SELECT COUNT(*) FROM trades", engine).iloc[0,0]
        st.metric("Total Trades", trades_count)
    except:
        st.metric("Total Trades", 0)

with col2:
    try:
        sentiment_avg = pd.read_sql("SELECT AVG(sentiment_score) FROM sentiment_logs", engine).iloc[0,0]
        st.metric("Avg Sentiment", f"{sentiment_avg:.2f}" if sentiment_avg else "0.0")
    except:
        st.metric("Avg Sentiment", "0.0")

with col3:
    # Simulated Model Accuracy
    st.metric("ML Brain Accuracy", "68.4%", "+1.2%")

with col4:
    active_assets = 0 # Placeholder
    st.metric("Active Assets", active_assets, "Portfolio Diversity")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "💼 Portfolio", "🧠 AI Brain", "📝 Trade Log"])

with tab1:
    st.subheader("Equity Curve & Trades")
    try:
        trades_df = pd.read_sql("SELECT * FROM trades", engine)
        if not trades_df.empty:
            # Simple simulation of equity
            trades_df['value'] = trades_df.apply(lambda x: x['price'] * x['quantity'] * (1 if x['side']=='BUY' else -1), axis=1)
            trades_df['cumulative'] = trades_df['value'].cumsum()

            fig = px.line(trades_df, x='timestamp', y='cumulative', title='Simulated Cumulative Cashflow')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trades executed yet.")
    except Exception as e:
        st.error(f"Error loading trades: {e}")

with tab2:
    st.subheader("Portfolio Allocation")
    try:
        # Calculate current holdings from trades (simplified)
        trades_df = pd.read_sql("SELECT * FROM trades", engine)
        if not trades_df.empty:
            holdings = {}
            for _, row in trades_df.iterrows():
                sym = row['symbol']
                qty = row['quantity'] * (1 if row['side']=='BUY' else -1)
                holdings[sym] = holdings.get(sym, 0) + qty

            # Filter non-zero
            holdings = {k: v for k, v in holdings.items() if v > 0}

            if holdings:
                labels = list(holdings.keys())
                values = list(holdings.values())
                fig_pie = px.pie(values=values, names=labels, title="Current Allocation")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Portfolio is currently 100% Cash.")
        else:
            st.info("No active positions.")
    except Exception as e:
        st.error(f"Portfolio Error: {e}")

with tab3:
    st.subheader("Inside the Machine Learning Brain")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Feature Importance")
        # Hardcoded for visualization of the concept
        features = pd.DataFrame({
            'Feature': ['RSI', 'Sentiment Score', 'ATR (Vol)', 'MACD'],
            'Importance': [0.35, 0.30, 0.20, 0.15]
        })
        fig_feat = px.bar(features, x='Importance', y='Feature', orientation='h')
        st.plotly_chart(fig_feat, use_container_width=True)

    with col_b:
        st.markdown("#### Sentiment Distribution")
        try:
            sent_df = pd.read_sql("SELECT sentiment_score FROM sentiment_logs", engine)
            if not sent_df.empty:
                fig_hist = px.histogram(sent_df, x="sentiment_score", nbins=20)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No sentiment data logged yet.")
        except:
            pass

with tab4:
    st.subheader("Recent Activity")
    try:
        logs_df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50", engine)
        st.dataframe(logs_df, use_container_width=True)
    except:
        st.info("No logs available")
