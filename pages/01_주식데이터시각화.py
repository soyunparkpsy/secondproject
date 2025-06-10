import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.title('글로벌 시총 Top 10 기업 주가 변화 시각화 (최근 3년)')

# --- Step 1: 현재 시점의 글로벌 시총 Top 10 기업 티커를 여기에 입력하세요 ---
# 이 리스트는 수동으로 업데이트해야 합니다.
top_10_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    # 필요에 따라 다른 Top 10 기업 추가
    # "Saudi Aramco": "2222.SR", # 사우디 아람코는 티커가 다를 수 있습니다.
    # "Meta Platforms": "META",
    # "Tesla": "TSLA",
    # "Berkshire Hathaway": "BRK-A",
    # "Johnson & Johnson": "JNJ"
}
# --------------------------------------------------------------------------

# 날짜 범위 설정 (최근 3년)
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=3*365) # 대략 3년

st.write(f"데이터 조회 기간: {start_date} 부터 {end_date} 까지")

# 모든 기업의 주가 데이터를 저장할 DataFrame
all_stocks_df = pd.DataFrame()

# 각 기업의 주가 데이터 가져오기
for company_name, ticker in top_10_tickers.items():
    try:
        # auto_adjust=False를 추가하여 'Adj Close' 컬럼을 명시적으로 가져오도록 합니다.
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        
        if not data.empty and 'Adj Close' in data.columns:
            data['Company'] = company_name
            data['Ticker'] = ticker
            all_stocks_df = pd.concat([all_stocks_df, data[['Adj Close', 'Company', 'Ticker']]], axis=0)
        else:
            st.warning(f"{company_name} ({ticker}) 에 대한 데이터를 가져올 수 없거나 'Adj Close' 컬럼이 없습니다.")
    except Exception as e:
        st.error(f"{company_name} ({ticker}) 데이터 로딩 중 오류 발생: {e}")

if not all_stocks_df.empty:
    # 'Adj Close' (수정 종가)를 기준으로 피봇 테이블 생성하여 시각화 용이하게 변경
    pivot_df = all_stocks_df.pivot_table(index=all_stocks_df.index, columns='Company', values='Adj Close')

    # 모든 주가를 첫날 가격 기준으로 정규화하여 변화율 비교
    # 데이터가 비어있지 않은지 다시 한번 확인 후 정규화 수행
    if not pivot_df.empty:
        normalized_df = pivot_df / pivot_df.iloc[0] * 100

        st.subheader('최근 3년 글로벌 시총 Top 기업 주가 변화 (정규화)')
        st.line_chart(normalized_df)

        st.subheader('각 기업별 주가 변화 (정규화)')
        selected_company = st.selectbox('기업 선택:', list(top_10_tickers.keys()))

        if selected_company in normalized_df.columns:
            st.line_chart(normalized_df[[selected_company]])
        else:
            st.warning("선택된 기업의 데이터가 없습니다.")

        st.subheader('원시 주가 데이터 (수정 종가)')
        st.dataframe(pivot_df)
    else:
        st.info("시각화할 주가 데이터가 없습니다. 가져온 데이터가 비어 있습니다.")

else:
    st.info("시각화할 주가 데이터가 없습니다. Top 10 기업 티커를 확인해주세요.")

st.markdown("""
---
**참고:**
* 글로벌 시가총액 Top 10 기업은 실시간으로 변동하므로, 정확한 티커 리스트를 확인 후 `top_10_tickers` 변수를 업데이트해야 합니다.
* `yfinance`는 일부 비미국 주식에 대해 티커가 다를 수 있습니다 (예: 사우디 아람코).
* 데이터 로딩에 실패하는 경우 인터넷 연결 상태 및 티커 정확성을 확인해주세요.
* `yfinance` 버전이 업데이트되면서 `yf.download()` 함수의 동작이 변경될 수 있으니, 오류 발생 시 `auto_adjust=False`와 같은 파라미터 추가를 고려하세요.
""")
