import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="글로벌 Top 기업 주가 시각화",
    page_icon="📈",
    layout="wide"
)

st.title('글로벌 시총 Top 기업 주가 변화 시각화')
st.markdown("""
선택된 글로벌 기업들의 지난 3년간 주가 변화를 보여줍니다.
데이터 로딩에 문제가 있을 경우 자동으로 재시도합니다.
""")

# --- 기업 티커 목록 (필요시 업데이트) ---
TOP_COMPANIES_TICKERS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Meta Platforms": "META",
    "Tesla": "TSLA",
    "Broadcom": "AVGO",
    "Johnson & Johnson": "JNJ",
    "Samsung Electronics": "005930.KS", # 한국 주식 예시
    "Saudi Aramco": "2222.SR" # 사우디 아람코 예시
}

# --- 데이터 조회 기간 설정 (오늘 날짜로부터 3일 전까지 3년치 데이터) ---
END_DATE = datetime.date.today() - datetime.timedelta(days=3)
START_DATE = END_DATE - datetime.timedelta(days=3 * 365 + 5) # 3년 + 여유 5일
st.info(f"✨ **데이터 조회 기간:** `{START_DATE}` 부터 `{END_DATE}` 까지")

# --- 주가 데이터 로딩 함수 (캐싱 적용) ---
@st.cache_data(ttl=3600, show_spinner=False) # 1시간 캐시, 내장 스피너 끔
def load_stock_data(tickers, start, end, max_retries=5, retry_delay=7):
    all_close_data = {}
    progress_text = "🚀 **주식 데이터를 불러오고 있습니다...**"
    progress_bar = st.progress(0, text=progress_text)
    
    total_tickers = len(tickers)
    for i, (company_name, ticker) in enumerate(tickers.items()):
        attempts = 0
        data_loaded = False
        while attempts < max_retries:
            try:
                # auto_adjust=True로 조정된 'Close' 가격을 직접 가져옴
                data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
                
                if not data.empty and 'Close' in data.columns:
                    all_close_data[company_name] = data['Close'].rename(company_name)
                    st.success(f"✔️ **{company_name}** (`{ticker}`) 데이터 로드 성공!")
                    data_loaded = True
                    break
                else:
                    st.warning(f"⚠️ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 데이터가 없거나 'Close' 컬럼을 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"❌ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 오류: {e}")
            
            attempts += 1
            if attempts < max_retries:
                time.sleep(retry_delay)
        
        if not data_loaded:
            st.error(f"🔴 **{company_name}** (`{ticker}`) 데이터 로드 실패. 티커를 확인해주세요.")
        
        progress_bar.progress((i + 1) / total_tickers, text=f"✨ **{company_name}** 데이터 로딩 중...")
    
    progress_bar.empty()
    return all_close_data

# --- 데이터 로딩 실행 ---
with st.spinner("⏳ 데이터 불러오는 중... 잠시만 기다려 주세요."):
    stock_data = load_stock_data(TOP_COMPANIES_TICKERS, START_DATE, END_DATE)

# --- 데이터 처리 및 시각화 ---
if stock_data:
    # Series들을 합쳐 DataFrame 생성 (날짜 기준으로 자동 정렬 및 NaN 채움)
    raw_df = pd.concat(stock_data.values(), axis=1)
    raw_df.columns = stock_data.keys()
    raw_df = raw_df.dropna(how='all') # 모든 값이 NaN인 행 제거

    if not raw_df.empty:
        # 정규화된 주가 데이터 생성 (각 컬럼의 첫 유효값 기준)
        initial_values = pd.Series(dtype='float64')
        for col in raw_df.columns:
            first_valid_val_idx = raw_df[col].first_valid_index()
            if first_valid_val_idx is not None:
                initial_values[col] = raw_df.loc[first_valid_val_idx, col]
            else:
                initial_values[col] = pd.NA
        
        normalized_df = pd.DataFrame()
        valid_initial_values = initial_values.dropna()

        if not valid_initial_values.empty:
            normalized_df = raw_df[valid_initial_values.index] / valid_initial_values * 100
            normalized_df = normalized_df.dropna(axis=1, how='all') # 모든 값이 NaN인 컬럼 제거
        else:
            st.warning("정규화를 위한 초기 유효값을 찾을 수 없습니다. 모든 데이터가 비어있을 수 있습니다.")
        
        # --- 시각화 ---
        if not normalized_df.empty:
            st.subheader('📊 지난 3년간 글로벌 Top 기업 주가 변화 (정규화)')
            st.line_chart(normalized_df)

            st.subheader('🔍 개별 기업 주가 변화 상세 보기 (정규화)')
            selectable_companies = normalized_df.columns.tolist()
            if selectable_companies:
                selected_company = st.selectbox('기업을 선택하세요:', selectable_companies)
                if selected_company:
                    st.line_chart(normalized_df[[selected_company]])
            else:
                st.warning("선택할 수 있는 기업 데이터가 없습니다. 데이터 로딩에 실패했을 수 있습니다.")

            st.subheader('📋 원시 주가 데이터 (조정 종가)')
            st.dataframe(raw_df)
        else:
            st.info("⚠️ 정규화된 주가 데이터를 생성할 수 없습니다. 원시 데이터를 확인해주세요.")
    else:
        st.info("⚠️ 데이터 로딩은 성공했으나, 유효한 거래일 데이터가 없습니다.")

else:
    st.error("❌ 시각화할 주가 데이터가 없습니다. 티커를 확인하거나, 데이터 로딩 오류를 해결해주세요.")

---
### 💡 참고 사항

* `SyntaxError`는 코드 문법 자체의 문제입니다. 이 코드를 복사-붙여넣기 할 때 **줄바꿈, 들여쓰기, 따옴표, 괄호** 등이 정확하게 유지되었는지 꼭 확인해주세요.
* 가장 확실한 방법은 이 코드를 **로컬 환경에서 먼저 실행**하여 `SyntaxError`가 발생하는지 확인하고, 발생한다면 정확한 오류 메시지를 파악하는 것입니다.
* `requirements.txt` 파일에 `streamlit`, `yfinance==0.2.38`, `pandas`가 정확히 명시되어 있는지 다시 한번 확인하고 Streamlit Cloud에서 재배포해주세요.

이 코드가 정상적으로 작동하여 멋진 시각화를 볼 수 있기를 바랍니다!
