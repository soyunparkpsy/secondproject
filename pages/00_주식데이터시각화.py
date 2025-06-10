import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("글로벌 시총 Top 10 기업 주가 변화 시각화 (최근 3년)")

# Define the top 10 companies and their tickers (as of June 2025 - approximate)
# Note: Market cap ranks fluctuate. This is a representative list.
# Using BRK-B for Berkshire Hathaway as BRK-A is less liquid and very high price.
# Saudi Aramco (2222.SR) might have issues with yfinance depending on its API access for non-US stocks.
# If 2222.SR fails, you might replace it with 'TSLA' or 'WMT'.
companies = {
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta Platforms": "META",
    "Saudi Aramco": "2222.SR", # May need to be replaced if yfinance has issues
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B"
}

# Calculate date range for the last 3 years
end_date = datetime.now()
start_date = end_date - timedelta(days=3 * 365) # Approximately 3 years

@st.cache_data
def get_stock_data(ticker, start, end):
    """Fetches historical stock data for a given ticker."""
    try:
        data = yf.download(ticker, start=start, end=end)
        return data['Adj Close']
    except Exception as e:
        st.warning(f"데이터를 가져오는 데 실패했습니다: {ticker} ({e})")
        return pd.Series()

# Create a list to hold the stock data
all_stock_data = {}

# Fetch data for each company
with st.spinner("최근 3년 주가 데이터를 불러오는 중..."):
    for name, ticker in companies.items():
        st.write(f"fetching {name} ({ticker})...")
        stock_data = get_stock_data(ticker, start_date, end_date)
        if not stock_data.empty:
            all_stock_data[name] = stock_data
        else:
            st.error(f"{name} ({ticker}) 데이터를 가져올 수 없습니다. 다음 종목으로 넘어갑니다.")

if not all_stock_data:
    st.error("데이터를 가져온 기업이 없습니다. 티커를 확인하거나 인터넷 연결을 확인해주세요.")
else:
    # Combine all stock data into a single DataFrame
    df_combined = pd.DataFrame(all_stock_data)

    # Normalize data to show percentage change from the start date
    # This makes it easier to compare performance across different stock prices
    df_normalized = df_combined.apply(lambda x: (x / x.iloc[0]) * 100 if not x.empty else x)

    st.subheader("최근 3년간 주가 변화 (시작일 기준 백분율)")

    # Plotting with Plotly
    fig = go.Figure()
    for col in df_normalized.columns:
        fig.add_trace(go.Scatter(x=df_normalized.index, y=df_normalized[col], mode='lines', name=col))

    fig.update_layout(
        title="글로벌 시총 Top 10 기업 주가 변화 (시작일 기준 100%)",
        xaxis_title="날짜",
        yaxis_title="주가 변화 (%)",
        hovermode="x unified",
        legend_title="기업",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("원시 주가 데이터 (조정 종가)")
    st.dataframe(df_combined)

    st.subheader("정규화된 주가 데이터 (시작일 기준 백분율)")
    st.dataframe(df_normalized)

st.markdown("""
---
**참고:**
* 주가 데이터는 `yfinance` 라이브러리를 통해 가져옵니다.
* "글로벌 시총 Top 10 기업" 목록은 시장 상황에 따라 변동될 수 있습니다. 본 시각화는 2025년 6월 기준의 대표적인 기업 목록을 사용합니다.
* 주가 변화는 시작일(3년 전)을 100%로 기준으로 하여 계산된 백분율입니다.
* `Saudi Aramco (2222.SR)` 데이터 로딩에 문제가 발생할 경우, 미국 증시에 상장된 다른 상위 기업(예: `TSLA` (Tesla) 또는 `WMT` (Walmart))으로 대체하는 것을 고려해보세요.
""")
