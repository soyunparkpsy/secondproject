import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="글로벌 Top 기업 주가 시각화",
    page_icon="📈",
    layout="wide"
)

st.title('글로벌 시총 Top 기업 주가 변화 시각화 (최근 3년)')
st.markdown("""
이 앱은 선택된 글로벌 시가총액 상위 기업들의 지난 3년간 주가 변화를 보여줍니다.
데이터 로딩 실패 시 재시도 로직이 포함되어 있습니다.
""")

# --- 2. 기업 티커 및 날짜 범위 설정 ---
# **주의: 이 리스트는 실시간으로 변동하는 시가총액 순위를 반영하지 않습니다.**
# 필요에 따라 최신 정보를 기반으로 업데이트해주세요.
TOP_COMPANIES_TICKERS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Meta Platforms": "META",
    "Tesla": "TSLA",
    "Broadcom": "AVGO", # 예시 추가
    "Johnson & Johnson": "JNJ", # 예시 추가
    "Samsung Electronics": "005930.KS", # 한국 주식 예시 (티커 다름)
    "Saudi Aramco": "2222.SR" # 사우디 아람코 예시 (티커 다름)
}

# 날짜 범위 설정: 오늘 날짜에서 하루 전을 종료일로, 3년 전을 시작일로 설정
# yfinance가 당일 데이터를 즉시 제공하지 않을 수 있어 안정성을 높임
END_DATE = datetime.date.today() - datetime.timedelta(days=1)
START_DATE = END_DATE - datetime.timedelta(days=3 * 365) # 대략 3년

st.info(f"✨ **데이터 조회 기간:** `{START_DATE}` 부터 `{END_DATE}` 까지")

# --- 3. 주가 데이터 로딩 함수 ---
# @st.cache_data 데코레이터를 사용하여 데이터 로딩 속도 향상 및 재실행 방지
# 인자가 변경되지 않으면 캐시된 데이터를 사용
@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신
def load_stock_data(tickers, start, end, max_retries=3, retry_delay=5):
    """
    주가 데이터를 yfinance에서 가져오는 함수.
    데이터 로딩 실패 시 재시도 로직을 포함합니다.
    """
    all_adj_close_data = {}
    st.subheader("데이터 로딩 중...")
    progress_bar = st.progress(0)
    
    total_tickers = len(tickers)
    for i, (company_name, ticker) in enumerate(tickers.items()):
        attempts = 0
        data_loaded = False
        while attempts < max_retries:
            try:
                # auto_adjust=True: 배당 및 분할이 조정된 최종 'Close' 가격을 직접 반환
                # 이렇게 하면 'Adj Close' 컬럼이 없는 문제를 피할 수 있으며,
                # 반환되는 데이터프레임에는 'Open', 'High', 'Low', 'Close', 'Volume'만 포함됩니다.
                data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
                
                if not data.empty and 'Close' in data.columns:
                    all_adj_close_data[company_name] = data['Close'].rename(company_name)
                    st.success(f"✔️ **{company_name}** (`{ticker}`) 데이터 로드 성공!")
                    data_loaded = True
                    break # 데이터 로딩 성공, 재시도 루프 탈출
                else:
                    st.warning(f"⚠️ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 데이터가 비어있거나 'Close' 컬럼을 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"❌ 시도 {attempts + 1}/{max_retries}: {company_name} (`{ticker}`) 데이터 로딩 중 오류 발생: {e}")
            
            attempts += 1
            time.sleep(retry_delay) # 재시도 전 잠시 대기 (서버 부하 감소)
        
        if not data_loaded:
            st.error(f"🔴 **{company_name}** (`{ticker}`) 데이터를 {max_retries}번 시도 후에도 가져오지 못했습니다. 티커를 확인해주세요.")
        
        progress_bar.progress((i + 1) / total_tickers)
    
    progress_bar.empty() # 진행률 바 제거
    return all_adj_close_data

# --- 4. 데이터 로딩 실행 ---
with st.spinner("🚀 주식 데이터를 불러오고 있습니다..."):
    stock_data = load_stock_data(TOP_COMPANIES_TICKERS, START_DATE, END_DATE)

# --- 5. 데이터 처리 및 시각화 ---
if stock_data: # 하나라도 성공적으로 로드된 데이터가 있다면
    # 딕셔너리의 Series들을 concat하여 DataFrame 생성
    # 이때 인덱스(날짜)를 기준으로 자동으로 정렬되며, 누락된 날짜는 NaN으로 채워집니다.
    raw_df = pd.concat(stock_data.values(), axis=1)
    raw_df.columns = stock_data.keys() # 컬럼 이름을 기업 이름으로 설정

    if not raw_df.empty:
        # 모든 값이 NaN인 행은 제거 (거래가 없는 날짜)
        raw_df = raw_df.dropna(how='all')

        if not raw_df.empty:
            # 정규화된 주가 데이터 생성 (첫 유효값 기준)
            # 각 컬럼(기업)의 첫 번째 유효한 값을 찾아 이를 100으로 설정하여 정규화
            normalized_df = pd.DataFrame()
            if not raw_df.empty:
                # 각 컬럼의 첫 번째 유효한 값으로 나누어 정규화
                # 주의: 첫 번째 유효한 인덱스가 다를 수 있으므로, 각 컬럼별로 첫 유효값을 찾아서 나눔
                initial_values = raw_df.apply(lambda col: col.dropna().iloc[0] if not col.dropna().empty else pd.NA)
                
                # initial_values에 NaN이 아닌 값이 있는 컬럼만 정규화 대상
                valid_initial_values = initial_values.dropna()

                if not valid_initial_values.empty:
                    normalized_df = raw_df[valid_initial_values.index] / valid_initial_values * 100
                    # 정규화 후에도 모든 값이 NaN인 컬럼이 있다면 제거
                    normalized_df = normalized_df.dropna(axis=1, how='all')
                else:
                    st.warning("경고: 정규화를 위한 초기 유효값을 찾을 수 없습니다. 모든 데이터가 NaN일 수 있습니다.")
            
            if not normalized_df.empty:
                st.subheader('📊 지난 3년간 글로벌 Top 기업 주가 변화 (정규화)')
                st.line_chart(normalized_df)

                st.subheader('🔍 개별 기업 주가 변화 상세 보기 (정규화)')
                # normalized_df의 실제 컬럼에서 선택 가능한 기업 리스트 생성
                selectable_companies = normalized_df.columns.tolist()
                if selectable_companies:
                    selected_company = st.selectbox('기업을 선택하세요:', selectable_companies)
                    if selected_company:
                        st.line_chart(normalized_df[[selected_company]])
                else:
                    st.warning("선택할 수 있는 기업 데이터가 없습니다. 모든 기업의 데이터 로딩에 실패했을 수 있습니다.")

                st.subheader('📋 원시 주가 데이터 (조정 종가)')
                st.dataframe(raw_df)
            else:
                st.info("⚠️ 정규화된 주가 데이터를 생성할 수 없습니다. 원시 데이터를 확인해주세요.")
        else:
            st.info("⚠️ 데이터 로딩은 성공했으나, 유효한 거래일 데이터가 없습니다.")
    else:
        st.info("⚠️ 성공적으로 데이터를 가져왔으나, 최종 데이터 프레임이 비어 있습니다. 모든 기업의 데이터가 누락되었을 수 있습니다.")

else:
    st.error("❌ 시각화할 주가 데이터가 없습니다. 티커를 확인하거나, 데이터 로딩 오류를 해결해주세요.")

st.markdown("---")
st.markdown("""
**참고 사항:**
* 글로벌 시가총액 Top 기업은 실시간으로 변동합니다. `TOP_COMPANIES_TICKERS` 변수를 주기적으로 업데이트하는 것이 좋습니다.
* `yfinance`는 비공식 Yahoo Finance API를 사용하므로, 간헐적인 서비스 불안정이나 요청 제한이 있을 수 있습니다. 재시도 로직이 이를 완화하는 데 도움을 줍니다.
* 한국 주식(`005930.KS`)이나 사우디 아람코(`2222.SR`)처럼 미국 외 주식은 티커 형식이 다를 수 있으니 주의하세요.
""")
