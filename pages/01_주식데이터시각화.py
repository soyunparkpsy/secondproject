import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.title('글로벌 시총 Top 10 기업 주가 변화 시각화 (최근 3년)')

top_10_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
}

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=3*365)

st.write(f"데이터 조회 기간: {start_date} 부터 {end_date} 까지")

all_stocks_data = {} # 딕셔너리로 각 기업 데이터를 저장

for company_name, ticker in top_10_tickers.items():
    try:
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        
        if not data.empty and 'Adj Close' in data.columns:
            all_stocks_data[company_name] = data['Adj Close']
        else:
            st.warning(f"{company_name} ({ticker}) 에 대한 데이터를 가져올 수 없거나 'Adj Close' 컬럼이 없습니다.")
    except Exception as e:
        st.error(f"{company_name} ({ticker}) 데이터 로딩 중 오류 발생: {e}")

if all_stocks_data: # 데이터가 하나라도 성공적으로 로드되었다면
    # 딕셔너리를 DataFrame으로 변환
    # 이 과정에서 컬럼 이름이 'Company' 이름으로 직접 매핑됩니다.
    pivot_df = pd.DataFrame(all_stocks_data)

    if not pivot_df.empty:
        # 첫날 가격 기준으로 정규화
        normalized_df = pivot_df / pivot_df.iloc[0] * 100

        # 디버깅을 위한 출력 (실제 배포시에는 주석 처리 또는 삭제)
        st.write("--- normalized_df.head() (for debugging) ---")
        st.write(normalized_df.head())
        st.write("--- normalized_df.columns (for debugging) ---")
        st.write(normalized_df.columns)

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
        st.info("모든 기업의 데이터를 가져왔으나, 최종 데이터 프레임이 비어 있습니다.")
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
