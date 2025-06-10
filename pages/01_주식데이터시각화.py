import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("글로벌 시가총액 TOP 10 기업 주가 변화 (최근 3년)")

# --- 1. 글로벌 시가총액 TOP 10 기업 티커 수동 정의 (정확한 최신 정보는 별도 확인 필요) ---
# 이 리스트는 변동될 수 있으므로, 실제 애플리케이션 배포 시 최신 정보로 업데이트하는 것이 좋습니다.
# 2025년 6월 현재 기준(예상)으로 임시 티커 사용
top_10_tickers = {
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "엔비디아": "NVDA",
    "알파벳 (구글)": "GOOGL", # 또는 GOOG
    "아마존": "AMZN",
    "사우디 아람코": "2222.SR", # 사우디 거래소 티커
    "메타 플랫폼스": "META",
    "버크셔 해서웨이": "BRK-B", # B클래스 주식
    "일라이 릴리": "LLY",
    "테슬라": "TSLA"
}

# --- 2. 날짜 범위 설정 (최근 3년) ---
end_date = datetime.now()
start_date = end_date - timedelta(days=3*365) # 대략 3년

st.write(f"**데이터 기간:** {start_date.strftime('%Y년 %m월 %d일')} 부터 {end_date.strftime('%Y년 %m월 %d일')} 까지")

# --- 3. 주가 데이터 가져오기 및 시각화 ---
all_data = pd.DataFrame()
failed_downloads = []

for name, ticker in top_10_tickers.items():
    st.subheader(f"{name} ({ticker})")
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            # 종가 (Close) 데이터만 사용
            close_prices = data['Close'].rename(name)
            if all_data.empty:
                all_data = pd.DataFrame(close_prices)
            else:
                all_data = pd.merge(all_data, close_prices, left_index=True, right_index=True, how='outer')

            # 개별 기업 주가 시각화 (선택 사항)
            fig_individual = px.line(data, y='Close', title=f'{name} ({ticker}) 주가 변화')
            st.plotly_chart(fig_individual, use_container_width=True)
        else:
            st.warning(f"**경고:** {name} ({ticker}) 에 대한 데이터를 찾을 수 없습니다. 티커를 확인해주세요.")
            failed_downloads.append(name)
    except Exception as e:
        st.error(f"**오류:** {name} ({ticker}) 데이터 다운로드 중 오류 발생: {e}")
        failed_downloads.append(name)

st.header("전체 TOP 10 기업 주가 변화 비교")

if not all_data.empty:
    # 모든 기업의 주가를 한 그래프에 시각화 (초기값을 100으로 정규화하여 비교)
    # 정규화하여 변화율을 비교하는 것이 더 의미 있을 수 있습니다.
    st.subheader("정규화된 주가 변화 (시작점 100 기준)")
    normalized_data = all_data / all_data.iloc[0] * 100

    fig_normalized = px.line(normalized_data,
                             title='글로벌 시가총액 TOP 10 기업 정규화된 주가 변화 (시작점 100 기준)',
                             labels={'value': '정규화된 주가 (시작점=100)', 'index': '날짜'})
    fig_normalized.update_layout(hovermode="x unified")
    st.plotly_chart(fig_normalized, use_container_width=True)

    st.subheader("실제 종가 비교")
    fig_raw = px.line(all_data,
                      title='글로벌 시가총액 TOP 10 기업 실제 종가 변화',
                      labels={'value': '종가', 'index': '날짜'})
    fig_raw.update_layout(hovermode="x unified")
    st.plotly_chart(fig_raw, use_container_width=True)
else:
    st.warning("다운로드 가능한 주식 데이터가 없습니다. 티커 목록을 확인해주세요.")

if failed_downloads:
    st.error(f"다음 기업의 데이터 다운로드에 실패했습니다: {', '.join(failed_downloads)}")

st.markdown("""
---
**참고:**
* 상위 10개 기업의 티커는 시시각각 변동될 수 있으므로, 실제 배포 시 최신 정보로 업데이트하는 것이 중요합니다.
* yfinance는 비공식 라이브러리이므로 데이터의 정확성 및 안정성에 한계가 있을 수 있습니다.
* 사우디 아람코(2222.SR)와 같은 해외 거래소 주식은 yfinance에서 데이터를 제공하지 않을 수 있습니다.
* 데이터 다운로드 속도는 네트워크 환경 및 yfinance 서버 상태에 따라 달라질 수 있습니다.
""")
