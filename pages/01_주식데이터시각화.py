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
    # 필요에 따라 다른 Top 10 기업 추가
    # "Saudi Aramco": "2222.SR",
    # "Meta Platforms": "META",
    # "Tesla": "TSLA",
    # "Berkshire Hathaway": "BRK-A",
    # "Johnson & Johnson": "JNJ"
}

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=3*365)

st.write(f"데이터 조회 기간: {start_date} 부터 {end_date} 까지")

all_stocks_adj_close = {} # 각 기업의 Adj Close Series를 저장할 딕셔너리

for company_name, ticker in top_10_tickers.items():
    try:
        # auto_adjust=False를 추가하여 'Adj Close' 컬럼을 명시적으로 가져오도록 합니다.
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False) # progress=False 추가하여 터미널 출력 줄임
        
        if not data.empty and 'Adj Close' in data.columns:
            # Series의 이름을 기업 이름으로 설정 (필수 아님, 가독성 향상)
            all_stocks_adj_close[company_name] = data['Adj Close'].rename(company_name)
        else:
            st.warning(f"{company_name} ({ticker}) 에 대한 데이터를 가져올 수 없거나 'Adj Close' 컬럼이 없습니다. (데이터가 비어있을 수 있습니다.)")
    except Exception as e:
        st.error(f"{company_name} ({ticker}) 데이터 로딩 중 오류 발생: {e}")

if all_stocks_adj_close: # 하나라도 성공적으로 로드된 데이터가 있다면
    # 모든 Series를 합쳐 DataFrame 생성. 이때, 인덱스(날짜)가 서로 다르면 자동으로 NaN으로 채워짐.
    pivot_df = pd.concat(all_stocks_adj_close.values(), axis=1)
    pivot_df.columns = all_stocks_adj_close.keys() # 컬럼 이름을 기업 이름으로 설정

    if not pivot_df.empty:
        # 첫 번째 유효한 날짜의 가격을 기준으로 정규화
        # pivot_df.iloc[0] 대신 pivot_df.dropna().iloc[0] 또는 특정 날짜 기준으로 변경 가능
        # pivot_df.iloc[0]은 첫 번째 행을 가져오는데, 첫 번째 행의 모든 값이 NaN일 수 있으므로 주의
        
        # 첫 번째 유효한 행을 찾아서 정규화 (모든 컬럼에 대해 NaN이 아닌 첫 번째 행)
        first_valid_row = pivot_df.apply(lambda x: x.dropna().iloc[0] if not x.dropna().empty else None)
        
        # 만약 모든 기업이 첫날 데이터가 없다면 문제가 발생할 수 있으므로,
        # 정규화 기준이 되는 값이 None이 아닌 컬럼만 필터링
        valid_cols_for_normalization = first_valid_row.dropna().index
        
        if not valid_cols_for_normalization.empty:
            normalized_df = pivot_df[valid_cols_for_normalization] / first_valid_row[valid_cols_for_normalization] * 100
        else:
            normalized_df = pd.DataFrame() # 정규화할 데이터가 없으면 빈 DataFrame

        # 디버깅을 위한 출력 (실제 배포시에는 주석 처리 또는 삭제)
        st.write("--- pivot_df.head() (for debugging) ---")
        st.write(pivot_df.head())
        st.write("--- normalized_df.head() (for debugging) ---")
        st.write(normalized_df.head())
        st.write("--- normalized_df.columns (for debugging) ---")
        st.write(normalized_df.columns)

        if not normalized_df.empty:
            st.subheader('최근 3년 글로벌 시총 Top 기업 주가 변화 (정규화)')
            st.line_chart(normalized_df)

            st.subheader('각 기업별 주가 변화 (정규화)')
            # 선택 가능한 기업 리스트를 normalized_df의 컬럼에서 가져옴
            selectable_companies = [col for col in normalized_df.columns if col in top_10_tickers.keys()]
            if selectable_companies:
                selected_company = st.selectbox('기업 선택:', selectable_companies)
                st.line_chart(normalized_df[[selected_company]])
            else:
                st.warning("선택할 수 있는 기업 데이터가 없습니다.")

            st.subheader('원시 주가 데이터 (수정 종가)')
            st.dataframe(pivot_df)
        else:
            st.info("정규화된 주가 데이터가 없습니다. 원시 데이터를 확인해주세요.")
    else:
        st.info("성공적으로 데이터를 가져왔으나, 최종 데이터 프레임이 비어 있습니다.")

else:
    st.info("시각화할 주가 데이터가 없습니다. Top 10 기업 티커를 확인하거나 데이터 로딩 오류를 해결해주세요.")

st.markdown("""
---
**참고:**
* 글로벌 시가총액 Top 10 기업은 실시간으로 변동하므로, 정확한 티커 리스트를 확인 후 `top_10_tickers` 변수를 업데이트해야 합니다.
* `yfinance`는 일부 비미국 주식에 대해 티커가 다를 수 있습니다 (예: 사우디 아람코).
* 데이터 로딩에 실패하는 경우 인터넷 연결 상태 및 티커 정확성을 확인해주세요.
* `yfinance` 버전이 업데이트되면서 `yf.download()` 함수의 동작이 변경될 수 있으니, 오류 발생 시 `auto_adjust=False`와 같은 파라미터 추가를 고려하세요.
""")
