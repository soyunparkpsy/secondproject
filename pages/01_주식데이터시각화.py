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

# @st.cache_data를 사용하여 데이터를 캐싱합니다.
# 동일한 인수로 함수가 호출될 때 네트워크 요청 없이 캐시된 데이터를 사용합니다.
@st.cache_data(ttl=3600) # 1시간마다 캐시 갱신
def get_stock_data(ticker, start, end):
    """
    주어진 티커에 대한 과거 주식 데이터를 가져옵니다.
    데이터를 가져오는 데 실패하면 빈 Pandas Series를 반환합니다.
    """
    try:
        # yfinance.download() 시도
        data = yf.download(ticker, start=start, end=end, progress=False) # progress=False로 다운로드 진행바 숨김
        if not data.empty:
            # 여기를 'Adj Close'에서 'Close'로 변경했습니다.
            return data['Close']
        else:
            # 데이터프레임이 비어있는 경우 (예: 잘못된 티커, 데이터 없음)
            st.warning(f"경고: {ticker}에 대한 데이터를 찾을 수 없거나 데이터가 비어 있습니다.")
            return pd.Series()
    except Exception as e:
        # 데이터 가져오기 중 예외 발생 시 (네트워크 오류, API 문제 등)
        st.error(f"오류: {ticker} 데이터를 가져오는 데 실패했습니다. 자세한 내용: {e}")
        return pd.Series()

# Create a list to hold the stock data
all_stock_data = {}
failed_companies = [] # 데이터를 가져오는 데 실패한 기업을 추적

# Fetch data for each company
st.write("주가 데이터를 불러오는 중입니다. 잠시만 기다려 주세요...")
progress_bar = st.progress(0)
total_companies = len(companies)

for i, (name, ticker) in enumerate(companies.items()):
    st.info(f"'{name}' ({ticker}) 데이터 로딩 중...")
    stock_data = get_stock_data(ticker, start_date, end_date)
    if not stock_data.empty:
        all_stock_data[name] = stock_data
    else:
        failed_companies.append(name)
    progress_bar.progress((i + 1) / total_companies)

# 데이터 로딩 후 메시지 표시
if failed_companies:
    st.error(f"다음 기업의 데이터를 가져오는 데 실패했습니다: {', '.join(failed_companies)}. 잠시 후 다시 시도해 보세요.")
    st.warning("이는 YFiance의 일시적인 문제, 네트워크 연결 불량 또는 요청 제한 때문일 수 있습니다.")

if not all_stock_data:
    st.error("모든 기업의 데이터를 가져오는 데 실패했습니다. 티커를 확인하거나 인터넷 연결을 확인하고, 잠시 후 다시 시도해 주세요.")
else:
    # Combine all stock data into a single DataFrame
    df_combined = pd.DataFrame(all_stock_data)

    # Normalize data to show percentage change from the start date
    # This makes it easier to compare performance across different stock prices
    # 시작일의 데이터가 0이거나 NaN이면 문제가 발생할 수 있으므로 필터링
    df_normalized = df_combined.apply(lambda x: (x / x.iloc[0]) * 100 if not x.empty and x.iloc[0] != 0 else x)
    # NaN이 발생할 경우 0으로 채우거나 이전 값으로 채우는 등의 추가 처리 고려 가능

    st.subheader("최근 3년간 주가 변화 (시작일 기준 백분율)")

    # Plotting with Plotly
    fig = go.Figure()
    for col in df_normalized.columns:
        # 데이터가 NaN이 아닌 경우에만 플로팅
        if not df_normalized[col].dropna().empty:
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

    # 여기를 "원시 주가 데이터 (조정 종가)"에서 "원시 주가 데이터 (종가)"로 변경했습니다.
    st.subheader("원시 주가 데이터 (종가)")
    st.dataframe(df_combined)

    st.subheader("정규화된 주가 데이터 (시작일 기준 백분율)")
    st.dataframe(df_normalized)

st.markdown("""
---
**참고:**
* 주가 데이터는 `yfinance` 라이브러리를 통해 가져옵니다.
* **이 시각화는 배당금, 주식 분할 등을 조정한 '수정 종가'가 아닌, 실제 거래된 가격인 '종가'를 사용합니다.**
* "글로벌 시총 Top 10 기업" 목록은 시장 상황에 따라 변동될 수 있습니다. 본 시각화는 2025년 6월 기준의 대표적인 기업 목록을 사용합니다.
* 주가 변화는 시작일(3년 전)을 100%로 기준으로 하여 계산된 백분율입니다.
* 데이터 로딩에 문제가 발생할 경우, 이는 `yfinance`의 일시적인 API 제한 또는 Yahoo Finance 서버 문제일 가능성이 높습니다.
* `Saudi Aramco (2222.SR)` 데이터 로딩에 문제가 발생할 경우, 미국 증시에 상장된 다른 상위 기업(예: `TSLA` (Tesla) 또는 `WMT` (Walmart))으로 대체하는 것을 고려해보세요.
""")
