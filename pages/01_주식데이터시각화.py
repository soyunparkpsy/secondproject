import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time # time.sleep을 위해 추가

st.set_page_config(layout="wide") # 페이지 레이아웃을 넓게 설정
st.title('글로벌 시총 Top 기업 주가 변화 시각화 (최근 3년)')

# --- 1. 기업 티커 설정 ---
# 현재 시점의 글로벌 시총 Top 기업 티커를 여기에 입력하세요.
# 이 리스트는 실시간으로 변동하므로, 필요에 따라 업데이트해야 합니다.
top_10_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Meta Platforms": "META", # 예시 추가
    "Tesla": "TSLA", # 예시 추가
    "Saudi Aramco": "2222.SR", # 사우디 아람코 (티커가 다를 수 있음)
    "Berkshire Hathaway": "BRK-B", # BRK-A는 가격이 너무 높아 시각화에 부적합할 수 있으므로 B주 사용
    "Eli Lilly": "LLY" # 예시 추가
}

# --- 2. 날짜 범위 설정 ---
# 데이터 조회 기간을 최근 3년으로 설정합니다.
# yfinance가 당일 데이터를 즉시 제공하지 않을 수 있으므로, 종료일을 하루 전으로 설정합니다.
end_date = datetime.date.today() - datetime.timedelta(days=1)
start_date = end_date - datetime.timedelta(days=3 * 365) # 대략 3년

st.info(f"📈 **데이터 조회 기간:** {start_date} 부터 {end_date} 까지")

# --- 3. 주가 데이터 로딩 ---
all_stocks_adj_close = {} # 각 기업의 'Adj Close' Series를 저장할 딕셔너리
MAX_RETRIES = 3 # 최대 재시도 횟수
RETRY_DELAY = 5 # 재시도 간격 (초)

st.subheader("데이터 로딩 중...")
loading_bar = st.progress(0)
ticker_count = len(top_10_tickers)

for i, (company_name, ticker) in enumerate(top_10_tickers.items()):
    attempts = 0
    data_loaded = False
    while attempts < MAX_RETRIES:
        try:
            # auto_adjust=False로 'Adj Close' 컬럼을 명시적으로 가져오도록 시도
            # progress=False로 다운로드 진행 메시지 숨김
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
            
            if not data.empty and 'Adj Close' in data.columns:
                all_stocks_adj_close[company_name] = data['Adj Close'].rename(company_name)
                st.success(f"✔️ {company_name} ({ticker}) 데이터 로드 성공!")
                data_loaded = True
                break # 데이터 성공적으로 가져왔으므로 루프 탈출
            else:
                st.warning(f"⚠️ 시도 {attempts + 1}/{MAX_RETRIES}: {company_name} ({ticker}) 에 대한 데이터를 가져올 수 없거나 'Adj Close' 컬럼이 없습니다. (데이터가 비어있을 수 있습니다.)")
                attempts += 1
                time.sleep(RETRY_DELAY) # 재시도 전 잠시 대기
        except Exception as e:
            st.error(f"❌ 시도 {attempts + 1}/{MAX_RETRIES}: {company_name} ({ticker}) 데이터 로딩 중 오류 발생: {e}")
            attempts += 1
            time.sleep(RETRY_DELAY) # 재시도 전 잠시 대기
    
    if not data_loaded:
        st.error(f"🔴 {company_name} ({ticker}) 데이터를 {MAX_RETRIES}번 시도 후에도 가져오지 못했습니다.")
    
    loading_bar.progress((i + 1) / ticker_count)

loading_bar.empty() # 로딩 바 제거

# --- 4. 데이터 처리 및 시각화 ---
if all_stocks_adj_close: # 하나라도 성공적으로 로드된 데이터가 있다면
    # 모든 Series를 합쳐 DataFrame 생성 (인덱스(날짜)가 다르면 자동으로 NaN으로 채워짐)
    pivot_df = pd.concat(all_stocks_adj_close.values(), axis=1)
    pivot_df.columns = all_stocks_adj_close.keys() # 컬럼 이름을 기업 이름으로 설정

    if not pivot_df.empty:
        # 정규화된 주가 데이터 생성 (첫 유효값 기준)
        # 모든 컬럼에 대해 NaN이 아닌 첫 번째 값을 기준으로 정규화
        initial_values = pd.Series(dtype='float64')
        for col in pivot_df.columns:
            first_non_nan_idx = pivot_df[col].first_valid_index()
            if first_non_nan_idx is not None:
                initial_values[col] = pivot_df.loc[first_non_nan_idx, col]
            else:
                initial_values[col] = pd.NA # 해당 컬럼에 유효한 값이 없으면 NA

        normalized_df = pd.DataFrame()
        if not initial_values.dropna().empty: # 초기값이 있는 컬럼만 정규화
            normalized_df = pivot_df / initial_values * 100
            # 모든 값이 NaN인 컬럼은 제거 (예: 데이터 로딩 실패한 기업)
            normalized_df = normalized_df.dropna(axis=1, how='all')
        
        # 디버깅을 위한 출력 (실제 배포시에는 주석 처리 또는 삭제)
        # st.write("--- 원시 주가 데이터 (수정 종가) 일부 ---")
        # st.dataframe(pivot_df.head())
        # st.write("--- 정규화된 주가 데이터 일부 ---")
        # st.dataframe(normalized_df.head())
        # st.write("--- 정규화된 데이터 컬럼 ---")
        # st.write(normalized_df.columns.tolist())

        if not normalized_df.empty:
            st.subheader('📊 최근 3년 글로벌 시총 Top 기업 주가 변화 (정규화)')
            st.line_chart(normalized_df)

            st.subheader('🔍 각 기업별 주가 변화 상세 보기 (정규화)')
            selectable_companies = [col for col in normalized_df.columns if col in top_10_tickers.keys()]
            if selectable_companies:
                selected_company = st.selectbox('기업 선택:', selectable_companies)
                if selected_company:
                    st.line_chart(normalized_df[[selected_company]])
            else:
                st.warning("선택할 수 있는 기업 데이터가 없습니다. 모든 기업의 데이터 로딩에 실패했을 수 있습니다.")

            st.subheader('📋 원시 주가 데이터 (수정 종가)')
            st.dataframe(pivot_df)
        else:
            st.info("⚠️ 정규화된 주가 데이터가 없습니다. 데이터를 다시 확인해주세요.")
    else:
        st.info("⚠️ 성공적으로 데이터를 가져왔으나, 최종 데이터 프레임이 비어 있습니다. 모든 기업의 데이터가 누락되었을 수 있습니다.")

else:
    st.error("❌ 시각화할 주가 데이터가 없습니다. Top 기업 티커를 확인하거나, 데이터 로딩 오류를 해결해주세요.")

---

### 배포 전 확인 사항

1.  **`requirements.txt` 파일 업데이트:**
    Streamlit Cloud에 배포하기 전에, GitHub 저장소의 `requirements.txt` 파일에 다음 내용이 포함되어 있는지 확인하세요.
    ```
    streamlit
    yfinance==0.2.38 # 현재 가장 안정적인 버전으로 명시
    pandas
    ```
    (더 최신 버전이 나왔고 안정적이라고 판단되면 `yfinance>=0.2.38`로 변경할 수 있습니다.)

2.  **로컬 테스트:**
    코드를 로컬에서 먼저 실행하여 정상적으로 작동하는지 확인하는 것이 가장 중요합니다. 로컬에서 문제가 해결되면 Streamlit Cloud에 배포했을 때도 해결될 가능성이 높습니다.

3.  **Top 10 기업 티커 정확성:**
    `top_10_tickers` 딕셔너리에 있는 기업 티커가 정확한지 다시 한번 확인해주세요. 특히 해외 주식의 경우 티커 형식이 다를 수 있습니다 (예: 사우디 아람코의 `2222.SR`).

이 코드로 문제가 해결되기를 바랍니다! 추가적인 문제가 발생하면 알려주세요.
