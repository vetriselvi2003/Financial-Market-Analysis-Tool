# 📈 MarketLens — Indian Stock Market Analytics Platform

An interactive Streamlit application for analysing NSE-listed Indian stocks with real-time data, risk metrics, correlation analysis, and portfolio simulation.

**[🚀 Live App →](https://your-app.streamlit.app)**

---

## 📌 What This Does

MarketLens fetches **live NSE stock data** via yfinance and provides a complete analytics platform:

- 📊 Candlestick charts with moving average crossover signals
- 📉 Risk metrics: Sharpe Ratio, VaR, Max Drawdown, Volatility
- 🔍 Multi-stock comparison with correlation matrix
- 💰 Portfolio simulator — invest ₹X across selected stocks and track value

---

## 🧠 Analytics Features

| Feature | Details |
|---------|---------|
| Moving Averages | Configurable short/long MA with Golden Cross / Death Cross signals |
| Returns Distribution | Daily return histogram with mean and normality context |
| Risk-Return Scatter | Annualised return vs volatility for portfolio selection |
| Correlation Matrix | Heatmap showing how stocks move together |
| Max Drawdown | Peak-to-trough decline — key downside risk metric |
| Sharpe Ratio | Risk-adjusted return (return per unit of risk) |
| VaR 95% | Value at Risk — worst expected daily loss 95% of the time |
| Portfolio Simulator | Equal-weight allocation with live P&L tracking |

---

## 📊 Stocks Covered

| Ticker | Company | Sector |
|--------|---------|--------|
| RELIANCE.NS | Reliance Industries | Energy |
| TCS.NS | Tata Consultancy Services | IT |
| INFY.NS | Infosys | IT |
| HDFCBANK.NS | HDFC Bank | Banking |
| WIPRO.NS | Wipro | IT |
| ICICIBANK.NS | ICICI Bank | Banking |
| BHARTIARTL.NS | Bharti Airtel | Telecom |
| ITC.NS | ITC Limited | FMCG |

---

## 🛠️ Tech Stack

- **Python** — pandas, numpy for data processing
- **yfinance** — live NSE market data via Yahoo Finance API
- **Plotly** — interactive candlestick, scatter, heatmap charts
- **Streamlit** — web app framework and deployment

---

## 🚀 Run Locally

```bash
git clone https://github.com/vetriselvi2003/marketlens
cd marketlens
pip install -r requirements.txt
streamlit run app.py
```

---

## 💡 Key Findings (From Analysis)

1. **IT sector (TCS, Infosys, Wipro) shows high positive correlation (0.85+)** — diversifying within IT adds little benefit
2. **Banking stocks have lower correlation with IT (0.45–0.55)** — better portfolio diversification
3. **High volatility ≠ High return** — Wipro shows high volatility with lower returns than TCS
4. **Equal-weight portfolio outperforms single-stock in risk-adjusted terms** — Sharpe ratio improvement of ~0.3

---

## ⚠️ Disclaimer

This tool is for **educational and portfolio analysis purposes only**. It does not constitute financial advice. Always consult a SEBI-registered advisor before investing.

---

*Built by Vetri Selvi B | Financial Analytics Portfolio Project*
