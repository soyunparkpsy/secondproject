import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time # time.sleep을 위해 추가

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

# 날짜 범위 설정 (오늘 날짜보다 하루 전을 end_date로 설정하여 데이터 누락 가능성 줄임)
end_date = datetime.date.today() - datetime.timedelta(days=1) # 오늘 날짜에서 하루 빼기
start_date = end_date - datetime.timedelta(days=3*365) # 대략 3년

st.write(f"데이터 조회 기간: {start_date} 부터 {end_date} 까지")

all_stocks_adj_close = {}
MAX_RETRIES = 3 # 최대 재시도 횟수
RETRY_DELAY = 5 # 재시도 간격 (초)

for company_name, ticker in top_10_tickers.items():
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            # auto_adjust=False를 유지하여 'Adj Close' 컬럼을 기대합니다.
            # 만약 'Adj Close'가 계속 없다면, auto_adjust=True로 변경 후 'Close'를 사용해 보세요.
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
            
            if not data.empty and 'Adj Close' in data.columns:
                all_stocks_adj_close[company_name] = data['Adj Close'].rename(company_name)
                break # 데이터 성공적으로 가져왔으므로 루프 탈출
            else:
                st.warning(f"Attempt {attempts + 1}/{MAX_RETRIES}: {company_name} ({ticker}) 에 대한 데이터를 가져올 수 없거나 'Adj Close' 컬럼이 없습니다. (데이터가 비어있을 수 있습니다.)")
                attempts += 1
                time.sleep(RETRY_DELAY) # 재시도 전 잠시 대기
        except Exception as e:
            st.error(f"Attempt {attempts + 1}/{MAX_RETRIES}: {company_name} ({ticker}) 데이터 로딩 중 오류 발생: {e}")
            attempts += 1
            time.sleep(RETRY_DELAY) # 재시도 전 잠시 대기
    
    if company_name not in all_stocks_adj_close:
        st.error(f"Failed to load data for {company_name} ({ticker}) after {MAX_RETRIES} attempts.")

if all_stocks_adj_close:
    pivot_df = pd.concat(all_stocks_adj_close.values(), axis=1)
    pivot_df.columns = all_stocks_adj_close.keys()

    if not pivot_df.empty:
        # 첫 번째 유효한 행을 찾아서 정규화
        first_valid_row = pivot_df.apply(lambda x: x.dropna().iloc[0] if not x.dropna().empty else None)
        valid_cols_for_normalization = first_valid_row.dropna().index
        
        if not valid_cols_for_normalization.empty:
            # 정규화하기 전에 NaN 값이 없는 행을 기준으로 first_valid_row를 계산하는 것이 더 안정적
            # pivot_df의 모든 행이 NaN인 컬럼은 정규화에서 제외될 수 있음
            # 먼저 pivot_df에서 NaN이 아닌 값으로만 이루어진 첫 행을 찾아봅니다.
            
            # 각 컬럼의 첫번째 유효한 값을 찾음
            initial_values = pivot_df.iloc[0] # 일단 첫 행을 가져오고
            # 만약 첫 행에 NaN이 있으면, 해당 컬럼의 다음 유효한 값을 찾도록 개선
            for col in pivot_df.columns:
                if pd.isna(initial_values[col]):
                    # 해당 컬럼에서 NaN이 아닌 첫 번째 값을 찾음
                    first_non_nan_idx = pivot_df[col].first_valid_index()
                    if first_non_nan_idx is not None:
                        initial_values[col] = pivot_df.loc[first_non_nan_idx, col]

            # 모든 초기값이 NaN인 경우를 대비
            if not initial_values.dropna().empty:
                normalized_df = pivot_df / initial_values * 100
                # 모든 컬럼에 대해 NaN으로만 이루어진 컬럼은 제거
                normalized_df = normalized_df.dropna(axis=1, how='all')
            else:
                normalized_df = pd.DataFrame()
        else:
            normalized_df = pd.DataFrame()

        # 디버깅을 위한 출력
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
