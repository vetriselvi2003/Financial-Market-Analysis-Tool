import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Try live data first, fall back to local CSV ───────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    try:
        import yfinance as yf
        tickers = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS',
                   'WIPRO.NS','ICICIBANK.NS','BHARTIARTL.NS','ITC.NS']
        names = {
            'RELIANCE.NS':'Reliance Industries','TCS.NS':'Tata Consultancy',
            'INFY.NS':'Infosys','HDFCBANK.NS':'HDFC Bank','WIPRO.NS':'Wipro',
            'ICICIBANK.NS':'ICICI Bank','BHARTIARTL.NS':'Bharti Airtel','ITC.NS':'ITC Limited'
        }
        sectors = {
            'RELIANCE.NS':'Energy','TCS.NS':'IT','INFY.NS':'IT',
            'HDFCBANK.NS':'Banking','WIPRO.NS':'IT','ICICIBANK.NS':'Banking',
            'BHARTIARTL.NS':'Telecom','ITC.NS':'FMCG'
        }
        raw = yf.download(tickers, period='3y', interval='1d', progress=False)
        dfs = []
        for t in tickers:
            df = raw['Close'][[t]].copy()
            df.columns = ['close']
            df['ticker'] = t
            df['name']   = names[t]
            df['sector'] = sectors[t]
            df['open']   = raw['Open'][t].values
            df['high']   = raw['High'][t].values
            df['low']    = raw['Low'][t].values
            df['volume'] = raw['Volume'][t].values
            df = df.reset_index().rename(columns={'Date':'date'})
            df['returns']     = df['close'].pct_change()
            df['cum_returns'] = (1 + df['returns'].fillna(0)).cumprod() - 1
            dfs.append(df)
        return pd.concat(dfs, ignore_index=True), True
    except Exception:
        df = pd.read_csv('market_data.csv', parse_dates=['date'])
        return df, False

df_all, is_live = load_data()

STOCK_META = df_all[['ticker','name','sector']].drop_duplicates().set_index('ticker')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MarketLens | Indian Stock Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #060b14;
    color: #cdd6f4;
}
.main { background-color: #060b14; }
[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1a2540;
}
[data-testid="stSidebar"] label {
    color: #6b7a99 !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.kpi-card {
    background: linear-gradient(135deg, #0d1626 0%, #111e35 100%);
    border: 1px solid #1a2540;
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
}
.kpi-val   { font-family:'Space Grotesk'; font-size:1.9rem; font-weight:700; }
.kpi-label { font-size:0.72rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-top:4px; }
.green { color: #50fa7b; }
.red   { color: #ff5555; }
.blue  { color: #8be9fd; }
.gold  { color: #f1fa8c; }
.tag {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:600; margin:2px;
}
.tag-it      { background:#1a2e4a; color:#8be9fd; border:1px solid #1e4060; }
.tag-banking { background:#1a2a1a; color:#50fa7b; border:1px solid #1e4020; }
.tag-energy  { background:#2d1e0a; color:#ffb86c; border:1px solid #4a2e0a; }
.tag-fmcg    { background:#2a1a2a; color:#ff79c6; border:1px solid #40204a; }
.tag-telecom { background:#1a2a2a; color:#8be9fd; border:1px solid #0a3a3a; }
.insight-box {
    background:#0d1626; border:1px solid #1a2540;
    border-left: 3px solid #8be9fd;
    border-radius:10px; padding:14px 18px; margin-bottom:10px;
    font-size:0.88rem; line-height:1.7;
}
.insight-box strong { color:#8be9fd; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
data_badge = "🟢 Live NSE Data" if is_live else "🟡 Simulated Data (Deploy for Live)"
st.markdown(f"""
<div style='padding:6px 0 20px 0;'>
  <span style='font-size:2rem; font-weight:700; letter-spacing:-0.03em;'>📈 MarketLens</span>
  <span style='font-size:0.85rem; color:#4a5568; margin-left:14px;'>Indian Stock Analytics Platform</span>
  <span style='font-size:0.72rem; color:#50fa7b; margin-left:14px; background:#0d2218; 
               padding:3px 10px; border-radius:20px; border:1px solid #1a4a2a;'>{data_badge}</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-size:1rem; font-weight:600; color:#cdd6f4; 
                padding-bottom:14px; border-bottom:1px solid #1a2540; margin-bottom:16px;'>
        Analysis Parameters
    </div>""", unsafe_allow_html=True)

    all_tickers = df_all['ticker'].unique().tolist()
    selected    = st.multiselect(
        "Select Stocks",
        options=all_tickers,
        default=['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFCBANK.NS'],
        format_func=lambda t: f"{STOCK_META.loc[t,'name']} ({t.replace('.NS','')})"
    )
    if not selected:
        selected = ['TCS.NS', 'INFY.NS']

    date_min = df_all['date'].min().date()
    date_max = df_all['date'].max().date()
    start_date = st.date_input("From", value=date_min, min_value=date_min, max_value=date_max)
    end_date   = st.date_input("To",   value=date_max, min_value=date_min, max_value=date_max)

    st.markdown("---")
    ma_short = st.slider("Short MA (days)", 10, 50, 20)
    ma_long  = st.slider("Long  MA (days)", 30, 200, 50)
    st.markdown("---")
    investment = st.number_input("Investment Amount (₹)", value=100000, step=10000)

# ── Filter data ───────────────────────────────────────────────────────────────
mask = (
    df_all['ticker'].isin(selected) &
    (df_all['date'] >= pd.Timestamp(start_date)) &
    (df_all['date'] <= pd.Timestamp(end_date))
)
df = df_all[mask].copy()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊  Price & Trend", "📉  Risk & Returns", "🔍  Stock Comparison", "💰  Portfolio Simulator"]
)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — PRICE & TREND
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    primary = selected[0]
    df_p    = df[df['ticker'] == primary].copy().sort_values('date')

    # Moving averages
    df_p[f'MA{ma_short}'] = df_p['close'].rolling(ma_short).mean()
    df_p[f'MA{ma_long}']  = df_p['close'].rolling(ma_long).mean()

    # KPI row
    latest     = df_p['close'].iloc[-1]
    prev       = df_p['close'].iloc[-2]
    start_p    = df_p['close'].iloc[0]
    day_chg    = (latest - prev) / prev * 100
    total_ret  = (latest - start_p) / start_p * 100
    volatility = df_p['returns'].std() * np.sqrt(252) * 100
    avg_vol    = df_p['volume'].mean()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, cls in [
        (c1, f"₹{latest:,.2f}",         "Current Price",   "blue"),
        (c2, f"{'▲' if day_chg>0 else '▼'} {abs(day_chg):.2f}%", "Day Change", "green" if day_chg>0 else "red"),
        (c3, f"{'▲' if total_ret>0 else '▼'} {abs(total_ret):.1f}%", "Period Return", "green" if total_ret>0 else "red"),
        (c4, f"{volatility:.1f}%",       "Ann. Volatility", "gold"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-val {cls}">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Candlestick + MA chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.04)

    fig.add_trace(go.Candlestick(
        x=df_p['date'], open=df_p['open'], high=df_p['high'],
        low=df_p['low'],  close=df_p['close'],
        name='OHLC',
        increasing_fillcolor='#50fa7b', increasing_line_color='#50fa7b',
        decreasing_fillcolor='#ff5555', decreasing_line_color='#ff5555',
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_p['date'], y=df_p[f'MA{ma_short}'],
        name=f'MA{ma_short}', line=dict(color='#f1fa8c', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_p['date'], y=df_p[f'MA{ma_long}'],
        name=f'MA{ma_long}',  line=dict(color='#ff79c6', width=1.5)), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df_p['date'], y=df_p['volume'], name='Volume',
        marker_color=np.where(df_p['close'] >= df_p['open'], '#50fa7b', '#ff5555'),
        opacity=0.6,
    ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor='#0b1220', bordercolor='#1a2540', font=dict(color='#8892a4', size=11)),
        height=500, margin=dict(t=20, b=10),
        font=dict(family='Space Grotesk', color='#cdd6f4'),
        title=dict(text=f"{STOCK_META.loc[primary,'name']} — Price, Moving Averages & Volume",
                   font=dict(size=14, color='#8be9fd')),
    )
    fig.update_xaxes(gridcolor='#111e35', color='#4a5568')
    fig.update_yaxes(gridcolor='#111e35', color='#4a5568')
    st.plotly_chart(fig, use_container_width=True)

    # MA crossover signals
    st.markdown('<div style="border-left:3px solid #f1fa8c; padding:10px 16px; background:#0d1626; border-radius:8px; font-size:0.85rem; color:#8892a4;">'
                f'<strong style="color:#f1fa8c;">📌 MA Signal:</strong> When the <strong style="color:#f1fa8c;">MA{ma_short}</strong> crosses above '
                f'<strong style="color:#ff79c6;">MA{ma_long}</strong>, it is a bullish signal (Golden Cross). '
                f'When it crosses below, it is a bearish signal (Death Cross). These crossovers are used by traders to time entries and exits.</div>',
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — RISK & RETURNS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        # Returns distribution
        df_p2 = df[df['ticker'] == primary].copy()
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df_p2['returns'].dropna() * 100,
            nbinsx=60,
            marker_color='#8be9fd', opacity=0.8,
            name='Daily Returns'
        ))
        fig_hist.add_vline(x=0, line_dash='dash', line_color='#ff5555', line_width=1.5)
        mean_ret = df_p2['returns'].mean() * 100
        fig_hist.add_vline(x=mean_ret, line_dash='dot', line_color='#50fa7b',
                           annotation_text=f'Mean: {mean_ret:.3f}%',
                           annotation_font_color='#50fa7b')
        fig_hist.update_layout(
            paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
            title=dict(text="Daily Returns Distribution", font=dict(color='#8be9fd', size=13)),
            xaxis=dict(title='Return %', color='#4a5568', gridcolor='#111e35'),
            yaxis=dict(title='Frequency', color='#4a5568', gridcolor='#111e35'),
            height=320, margin=dict(t=40, b=20),
            font=dict(family='Space Grotesk', color='#cdd6f4')
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_r:
        # Risk-Return scatter for all selected stocks
        risk_return = []
        for t in selected:
            dft = df[df['ticker'] == t].copy()
            if len(dft) < 20: continue
            ann_ret = dft['returns'].mean() * 252 * 100
            ann_vol = dft['returns'].std() * np.sqrt(252) * 100
            sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0
            risk_return.append({
                'ticker': t.replace('.NS',''),
                'name': STOCK_META.loc[t,'name'],
                'sector': STOCK_META.loc[t,'sector'],
                'ann_return': round(ann_ret, 2),
                'ann_vol':    round(ann_vol, 2),
                'sharpe':     round(sharpe, 3),
            })
        rr_df = pd.DataFrame(risk_return)

        color_map = {'IT':'#8be9fd','Banking':'#50fa7b','Energy':'#ffb86c','FMCG':'#ff79c6','Telecom':'#bd93f9'}
        fig_rr = go.Figure()
        for _, row in rr_df.iterrows():
            fig_rr.add_trace(go.Scatter(
                x=[row['ann_vol']], y=[row['ann_return']],
                mode='markers+text',
                marker=dict(size=18, color=color_map.get(row['sector'],'#cdd6f4'),
                            line=dict(color='#060b14', width=2)),
                text=[row['ticker']], textposition='top center',
                textfont=dict(size=11, color='#cdd6f4'),
                name=row['name'], showlegend=False,
                hovertemplate=f"<b>{row['name']}</b><br>Return: {row['ann_return']}%<br>Volatility: {row['ann_vol']}%<br>Sharpe: {row['sharpe']}<extra></extra>"
            ))
        fig_rr.update_layout(
            paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
            title=dict(text="Risk vs Return (Annualised)", font=dict(color='#8be9fd', size=13)),
            xaxis=dict(title='Annual Volatility %', color='#4a5568', gridcolor='#111e35'),
            yaxis=dict(title='Annual Return %', color='#4a5568', gridcolor='#111e35'),
            height=320, margin=dict(t=40, b=20),
            font=dict(family='Space Grotesk', color='#cdd6f4')
        )
        st.plotly_chart(fig_rr, use_container_width=True)

    # Risk metrics table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7rem; color:#8be9fd; text-transform:uppercase; letter-spacing:0.12em; border-left:3px solid #8be9fd; padding-left:10px; margin-bottom:12px;">Risk Metrics Summary</div>', unsafe_allow_html=True)

    metrics_rows = []
    for t in selected:
        dft = df[df['ticker']==t].copy().sort_values('date')
        if len(dft) < 20: continue
        rets = dft['returns'].dropna()
        ann_ret = rets.mean() * 252 * 100
        ann_vol = rets.std() * np.sqrt(252) * 100
        sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0
        # Max drawdown
        cum    = (1 + rets).cumprod()
        roll_max = cum.cummax()
        dd = ((cum - roll_max) / roll_max)
        max_dd = dd.min() * 100
        # VaR 95%
        var_95 = np.percentile(rets, 5) * 100
        total_r = (dft['close'].iloc[-1] - dft['close'].iloc[0]) / dft['close'].iloc[0] * 100
        metrics_rows.append({
            'Stock': STOCK_META.loc[t,'name'],
            'Sector': STOCK_META.loc[t,'sector'],
            'Total Return %': round(total_r, 1),
            'Ann. Return %': round(ann_ret, 1),
            'Ann. Volatility %': round(ann_vol, 1),
            'Sharpe Ratio': round(sharpe, 3),
            'Max Drawdown %': round(max_dd, 1),
            'VaR 95% (daily)': f"{round(var_95, 2)}%",
        })
    metrics_df = pd.DataFrame(metrics_rows)
    st.dataframe(
        metrics_df.style.background_gradient(subset=['Total Return %','Sharpe Ratio'], cmap='RdYlGn')
                        .background_gradient(subset=['Ann. Volatility %','Max Drawdown %'], cmap='RdYlGn_r'),
        use_container_width=True, hide_index=True
    )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — STOCK COMPARISON
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    # Normalised price comparison
    fig_norm = go.Figure()
    colors = ['#8be9fd','#50fa7b','#ffb86c','#ff79c6','#bd93f9','#f1fa8c','#ff5555','#6272a4']
    for i, t in enumerate(selected):
        dft = df[df['ticker']==t].copy().sort_values('date')
        if len(dft) < 2: continue
        norm = dft['close'] / dft['close'].iloc[0] * 100
        fig_norm.add_trace(go.Scatter(
            x=dft['date'], y=norm,
            name=STOCK_META.loc[t,'name'].split()[0],
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f"<b>{STOCK_META.loc[t,'name']}</b><br>%{{y:.1f}} (base=100)<extra></extra>"
        ))
    fig_norm.add_hline(y=100, line_dash='dash', line_color='#4a5568', line_width=1)
    fig_norm.update_layout(
        paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
        title=dict(text="Normalised Price Comparison (Base = 100)", font=dict(color='#8be9fd', size=14)),
        xaxis=dict(color='#4a5568', gridcolor='#111e35'),
        yaxis=dict(color='#4a5568', gridcolor='#111e35', title='Indexed Price'),
        legend=dict(bgcolor='#0b1220', bordercolor='#1a2540', font=dict(color='#8892a4')),
        height=380, margin=dict(t=40, b=10),
        font=dict(family='Space Grotesk', color='#cdd6f4')
    )
    st.plotly_chart(fig_norm, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        # Correlation heatmap
        pivot = df.pivot_table(index='date', columns='ticker', values='returns')
        pivot.columns = [c.replace('.NS','') for c in pivot.columns]
        corr = pivot.corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale='RdBu', zmid=0, zmin=-1, zmax=1,
            text=np.round(corr.values, 2), texttemplate='%{text}',
            textfont=dict(size=11, color='white'),
            colorbar=dict(tickfont=dict(color='#8892a4'))
        ))
        fig_corr.update_layout(
            paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
            title=dict(text="Return Correlation Matrix", font=dict(color='#8be9fd', size=13)),
            xaxis=dict(color='#8892a4'), yaxis=dict(color='#8892a4'),
            height=340, margin=dict(t=40, b=10),
            font=dict(family='Space Grotesk', color='#cdd6f4')
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_b:
        # Sector performance
        sector_perf = []
        for t in selected:
            dft = df[df['ticker']==t].sort_values('date')
            if len(dft) < 2: continue
            ret = (dft['close'].iloc[-1] - dft['close'].iloc[0]) / dft['close'].iloc[0] * 100
            sector_perf.append({'Sector': STOCK_META.loc[t,'sector'],
                                 'Stock': STOCK_META.loc[t,'name'].split()[0],
                                 'Return %': round(ret, 1)})
        sp_df = pd.DataFrame(sector_perf).sort_values('Return %', ascending=True)
        fig_bar = go.Figure(go.Bar(
            y=sp_df['Stock'], x=sp_df['Return %'], orientation='h',
            marker_color=np.where(sp_df['Return %'] >= 0, '#50fa7b', '#ff5555'),
            text=[f"{v:+.1f}%" for v in sp_df['Return %']], textposition='outside',
            textfont=dict(color='#cdd6f4', size=11)
        ))
        fig_bar.add_vline(x=0, line_color='#4a5568', line_width=1)
        fig_bar.update_layout(
            paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
            title=dict(text="Total Return by Stock", font=dict(color='#8be9fd', size=13)),
            xaxis=dict(color='#4a5568', gridcolor='#111e35', title='Return %'),
            yaxis=dict(color='#8892a4'),
            height=340, margin=dict(t=40, b=10, r=60),
            font=dict(family='Space Grotesk', color='#cdd6f4')
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — PORTFOLIO SIMULATOR
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-size:0.7rem; color:#8be9fd; text-transform:uppercase; letter-spacing:0.12em; border-left:3px solid #8be9fd; padding-left:10px; margin-bottom:16px;">Equal-Weight Portfolio Simulation</div>', unsafe_allow_html=True)

    # Equal weight portfolio
    weight = 1 / len(selected)
    alloc  = investment * weight

    portfolio_vals = []
    pivot_close = df.pivot_table(index='date', columns='ticker', values='close').sort_index()
    pivot_close.columns = [c for c in pivot_close.columns]

    for t in selected:
        if t not in pivot_close.columns: continue
        prices = pivot_close[t].dropna()
        shares = alloc / prices.iloc[0]
        vals   = prices * shares
        portfolio_vals.append(vals)

    if portfolio_vals:
        port_df = pd.concat(portfolio_vals, axis=1).sum(axis=1).reset_index()
        port_df.columns = ['date', 'value']
        port_df['return_pct'] = (port_df['value'] - investment) / investment * 100
        port_df['gain_loss']  = port_df['value'] - investment

        final_val  = port_df['value'].iloc[-1]
        total_gain = final_val - investment
        total_ret  = total_gain / investment * 100
        max_val    = port_df['value'].max()
        min_val    = port_df['value'].min()

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, cls in [
            (c1, f"₹{investment:,.0f}",                         "Invested",         "blue"),
            (c2, f"₹{final_val:,.0f}",                          "Current Value",    "green" if total_gain>=0 else "red"),
            (c3, f"{'▲' if total_gain>=0 else '▼'} ₹{abs(total_gain):,.0f}", "Gain / Loss", "green" if total_gain>=0 else "red"),
            (c4, f"{'▲' if total_ret>=0 else '▼'} {abs(total_ret):.1f}%",    "Total Return", "green" if total_ret>=0 else "red"),
        ]:
            with col:
                st.markdown(f'<div class="kpi-card"><div class="kpi-val {cls}">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Portfolio value over time
        fig_port = go.Figure()
        fig_port.add_trace(go.Scatter(
            x=port_df['date'], y=port_df['value'],
            fill='tozeroy', fillcolor='rgba(80,250,123,0.07)',
            line=dict(color='#50fa7b', width=2.5),
            name='Portfolio Value',
            hovertemplate="Date: %{x|%d %b %Y}<br>Value: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_port.add_hline(y=investment, line_dash='dash', line_color='#f1fa8c',
                           annotation_text=f"Invested: ₹{investment:,.0f}",
                           annotation_font_color='#f1fa8c')
        fig_port.update_layout(
            paper_bgcolor='#060b14', plot_bgcolor='#0b1220',
            title=dict(text=f"Portfolio Value Over Time — ₹{investment:,.0f} invested equally across {len(selected)} stocks",
                       font=dict(color='#8be9fd', size=13)),
            xaxis=dict(color='#4a5568', gridcolor='#111e35'),
            yaxis=dict(color='#4a5568', gridcolor='#111e35', title='Portfolio Value (₹)'),
            height=360, margin=dict(t=50, b=10),
            font=dict(family='Space Grotesk', color='#cdd6f4')
        )
        st.plotly_chart(fig_port, use_container_width=True)

        # Per-stock allocation table
        st.markdown('<div style="font-size:0.7rem; color:#8be9fd; text-transform:uppercase; letter-spacing:0.12em; border-left:3px solid #8be9fd; padding-left:10px; margin-bottom:12px;">Allocation Breakdown</div>', unsafe_allow_html=True)
        alloc_rows = []
        for t in selected:
            if t not in pivot_close.columns: continue
            prices = pivot_close[t].dropna()
            shares = alloc / prices.iloc[0]
            cur_val = shares * prices.iloc[-1]
            gain    = cur_val - alloc
            ret     = gain / alloc * 100
            alloc_rows.append({
                'Stock': STOCK_META.loc[t,'name'],
                'Sector': STOCK_META.loc[t,'sector'],
                'Allocated (₹)': f"₹{alloc:,.0f}",
                'Shares': round(shares, 4),
                'Buy Price': f"₹{prices.iloc[0]:,.2f}",
                'Current Price': f"₹{prices.iloc[-1]:,.2f}",
                'Current Value (₹)': f"₹{cur_val:,.0f}",
                'Gain/Loss': f"{'▲' if gain>=0 else '▼'} ₹{abs(gain):,.0f}",
                'Return %': f"{'▲' if ret>=0 else '▼'} {abs(ret):.1f}%",
            })
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:40px; padding:16px; border-top:1px solid #1a2540; 
            text-align:center; color:#4a5568; font-size:0.72rem;'>
    MarketLens · Indian Stock Analytics · Built with Python, yfinance & Streamlit
    · Data is for educational purposes only, not financial advice
</div>
""", unsafe_allow_html=True)