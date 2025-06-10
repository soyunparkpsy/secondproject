import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# --- 1. Streamlit 페이지 기본 설정 ---
st.set_page_config(
    page_title="글로벌 Top 기업 주가 시각화",
    page_icon="📈",
    layout="wide" # 넓은 화면 레이아웃 사용
)

st.title('글로벌 시총 Top 기업 주가 변화 시각화')
st.markdown("""
이 앱은 선택된 글로벌 시가총액 상위 기업들의 지난 3년간 주가 변화를 보여줍니다.
데이터 로딩에 문제가 있을 경우 자동으로 재시도하며, 캐싱을 통해 빠른 로딩을 지원합니다.
""")

# --- 2. 기업 티커 목록 정의 ---
# **주의: 이 리스트는 실시간 시가총액 순위를 반영하지 않습니다.**
# 필요에 따라 최신 정보를 기반으로 직접 업데이트해주세요.
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
    "Samsung Electronics": "005930.KS", # 한국 주식 티커 예시 (주의: yfinance에서 지원하지 않을 수 있음)
    "Saudi Aramco": "2222.SR" # 사우디 아람코 티커 예시 (주의: yfinance에서 지원하지 않을 수 있음)
}

# --- 3. 데이터 조회 기간 설정 ---
# yfinance가 당일 데이터를 즉시 제공하지 않을 수 있으므로, 종료일을 현재로부터 며칠 전으로 설정
# 예를 들어, 한국 시간 기준으로 3일 전으로 설정하면 대부분의 시장 마감 후 데이터가 포함될 가능성이 높습니다.
END_DATE = datetime.date.today() - datetime.timedelta(days=3) # 현재로부터 3일 전 날짜
START_DATE = END_DATE - datetime.timedelta(days=3 * 365 + 5) # 약 3년 + 여유 5일

st.info(f"✨ **데이터 조회 기간:** `{START_DATE}` 부터 `{END_DATE}` 까지")

# --- 4. 주가 데이터 로딩 함수 (캐싱 및 재시도 로직 포함) ---
# @st.cache_data 데코레이터를 사용하여 데이터 로딩 속도 향상 및 불필요한 재실행 방지
# ttl=3600: 캐시된 데이터를 1시간(3600초) 동안 유효하게 유지 (이후 자동 갱신 시도)
# show_spinner=False: Streamlit 내장 스피너 대신 수동으로 진행 바 및 메시지 처리
@st.cache_data(ttl=3600, show_spinner=False)
def load_stock_data(tickers_dict, start_date_obj, end_date_obj, max_retries=5, retry_delay_sec=7):
    """
    yfinance를 사용하여 주가 데이터를 로드하고, 실패 시 재시도합니다.
    """
    all_close_data = {} # 성공적으로 로드된 주가 데이터를 저장할 딕셔너리
    
    # 진행률 바 및 메시지 초기화
    progress_text = "🚀 **주식 데이터를 불러오고 있습니다...**"
    progress_bar = st.progress(0, text=progress_text)
    
    total_tickers = len(tickers_dict)
    
    for i, (company_name, ticker) in enumerate(tickers_dict.items()):
        attempts = 0
        data_loaded_successfully = False # 현재 기업의 데이터 로딩 성공 여부 플래그
        
        while attempts < max_retries:
            try:
                # yfinance.download 호출: auto_adjust=True로 설정하여 조정된 'Close' 가격을 직접 가져옴
                # 'Adj Close' 컬럼이 없는 문제를 방지하며, 데이터프레임에 'Close'만 포함되게 함
                data = yf.download(
                    ticker,
                    start=start_date_obj,
                    end=end_date_obj,
                    auto_adjust=True, # 배당 및 분할 조정된 'Close' 가격 반환
                    progress=False # 다운로드 진행 메시지 숨김
                )
                
                # 데이터가 비어있지 않고, 'Close' 컬럼이 존재하는지 확인
                if not data.empty and 'Close' in data.columns:
                    all_close_data[company_name] = data['Close'].rename(company_name)
                    st.success(f"✔️ **{company_name}** (`{ticker}`) 데이터 로드 성공!")
                    data_loaded_successfully = True
                    break # 성공적으로 로드했으므로 현재 기업의 재시도 루프 탈출
                else:
                    st.warning(f"⚠️ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 데이터가 비어있거나 'Close' 컬럼을 찾을 수 없습니다. (데이터가 없을 수 있습니다.)")
            except Exception as e:
                # 데이터 로딩 중 예외 발생 시 오류 메시지 출력
                st.error(f"❌ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 데이터 로딩 중 오류 발생: {e}")
            
            attempts += 1
            if attempts < max_retries: # 마지막 시도에서는 대기하지 않음
                time.sleep(retry_delay_sec) # 재시도 전 잠시 대기 (서버 부하 감소 목적)
        
        # 모든 재시도 후에도 데이터 로딩에 실패한 경우 최종 오류 메시지 출력
        if not data_loaded_successfully:
            st.error(f"🔴 **{company_name}** (`{ticker}`) 데이터를 {max_retries}번 시도 후에도 가져오지 못했습니다. 티커를 확인해주세요.")
        
        # 진행률 바 업데이트
        progress_bar.progress((i + 1) / total_tickers, text=f"✨ **{company_name}** 데이터 로딩 중...")
    
    progress_bar.empty() # 모든 작업 완료 후 진행률 바 제거
    return all_close_data

# --- 5. 데이터 로딩 실행 ---
with st.spinner("⏳ 주식 데이터를 불러오는 중입니다... 잠시만 기다려 주세요."):
    stock_data_results = load_stock_data(TOP_COMPANIES_TICKERS, START_DATE, END_DATE)

# --- 6. 데이터 처리 및 시각화 ---
if stock_data_results: # 하나라도 성공적으로 로드된 데이터가 있다면
    # 딕셔너리의 Series들을 합쳐 DataFrame 생성
    # pd.concat은 Series들의 인덱스(날짜)를 자동으로 정렬하고, 누락된 날짜에는 NaN을 채워 넣습니다.
    raw_prices_df = pd.concat(stock_data_results.values(), axis=1)
    raw_prices_df.columns = stock_data_results.keys() # 컬럼 이름을 기업 이름으로 설정
    
    # 모든 값이 NaN인 행은 제거 (예: 주말, 공휴일 등 거래가 없는 날짜)
    raw_prices_df = raw_prices_df.dropna(how='all')

    if not raw_prices_df.empty:
        # 주가 데이터를 정규화 (각 기업의 첫 번째 유효한 값을 100으로 기준)
        normalized_prices_df = pd.DataFrame()
        
        initial_values = pd.Series(dtype='float64')
        for col in raw_prices_df.columns:
            first_valid_idx = raw_prices_df[col].first_valid_index()
            if first_valid_idx is not None:
                initial_values[col] = raw_prices_df.loc[first_valid_idx, col]
            else:
                initial_values[col] = pd.NA # 유효한 값이 없으면 NA 처리
        
        valid_initial_values = initial_values.dropna() # 초기값이 있는 컬럼만 선택

        if not valid_initial_values.empty:
            # 정규화: 현재 가격 / 초기값 * 100
            # raw_prices_df에서 유효한 초기값이 있는 컬럼만 선택하여 정규화
            normalized_prices_df = raw_prices_df[valid_initial_values.index] / valid_initial_values * 100
            # 정규화 후에도 모든 값이 NaN인 컬럼이 있다면 제거 (데이터 로딩 실패한 기업 등)
            normalized_prices_df = normalized_prices_df.dropna(axis=1, how='all')
        else:
            st.warning("경고: 주가 정규화를 위한 초기 유효값을 찾을 수 없습니다. 모든 데이터가 NaN일 수 있습니다.")
        
        # --- 시각화 섹션 ---
        if not normalized_prices_df.empty:
            st.subheader('📊 지난 3년간 글로벌 Top 기업 주가 변화 (정규화)')
            st.line_chart(normalized_prices_df)

            st.subheader('🔍 개별 기업 주가 변화 상세 보기 (정규화)')
            # 정규화된 데이터프레임의 실제 컬럼에서 선택 가능한 기업 리스트 생성
            selectable_companies = normalized_prices_df.columns.tolist()
            if selectable_companies:
                selected_company = st.selectbox('기업을 선택하세요:', selectable_companies)
                if selected_company: # 사용자가 기업을 선택했을 경우에만 차트 표시
                    st.line_chart(normalized_prices_df[[selected_company]])
            else:
                st.warning("선택할 수 있는 기업 데이터가 없습니다. 모든 기업의 데이터 로딩에 실패했을 수 있습니다.")

            st.subheader('📋 원시 주가 데이터 (조정 종가)')
            st.dataframe(raw_prices_df)
        else:
            st.info("⚠️ 정규화된 주가 데이터를 생성할 수 없습니다. 원시 데이터를 확인해주세요.")
    else:
        st.info("⚠️ 데이터 로딩은 성공했으나, 유효한 거래일 데이터가 없습니다.")

else:
    st.error("❌ 시각화할 주가 데이터가 없습니다. `TOP_COMPANIES_TICKERS`를 확인하거나, 데이터 로딩 오류를 해결해주세요.")

st.markdown("---")
st.markdown("""
### 💡 참고 사항

* **`SyntaxError` 발생 시:** 이 코드는 파이썬 문법에 맞게 작성되었습니다. 만약 `SyntaxError`가 계속 발생한다면, 코드를 복사-붙여넣기 할 때 **줄바꿈, 들여쓰기, 따옴표, 괄호** 등이 정확하게 유지되었는지 다시 한번 확인해야 합니다. 가장 좋은 방법은 코드를 로컬 환경에서 실행하여 정확한 오류 위치를 파악하는 것입니다.
* **`yfinance` 버전:** `requirements.txt` 파일에 `yfinance==0.2.38` (혹은 `yfinance>=0.2.38`로 최신 버전 허용)이 명시되어 있는지 확인해주세요.
* **티커 정확성:** 한국 주식(`005930.KS`)이나 사우디 아람코(`2222.SR`)와 같은 미국 외 주식은 `yfinance`에서 지원하지 않거나 티커 형식이 다를 수 있습니다. 데이터 로딩 실패 시 해당 티커의 유효성을 확인해주세요.
""")
