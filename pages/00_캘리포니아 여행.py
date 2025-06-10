import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="캘리포니아 여행 가이드", layout="wide")

st.title("🌴 캘리포니아 여행 가이드")
st.markdown("""
미국 서부의 보석, **캘리포니아** 🏄‍♀️  
관광명소부터 현지인 맛집, 편안한 숙소, 그리고 편리한 교통 정보까지, 이 가이드 하나면 여행 준비 끝!
""")

# 캘리포니아 홍보 영상 (YouTube 임베드)
st.subheader("캘리포니아의 매력에 빠져보세요! 🎬")
# 여기에 실제 캘리포니아 홍보 영상의 YouTube ID를 넣어주세요.
video_id = "I6kvtPRnwc"  # YouTube 로고 영상 (임시)
st.video(f"https://www.youtube.com/watch?v=I6kvtPRnwc")
st.markdown("---")

# 관광지, 맛집, 숙소 데이터 (DataFrame으로 관리)
locations_data = {
    "name": [
        "샌프란시스코 금문교", "인앤아웃 버거 (In-N-Out)", "요세미티 국립공원",
        "필즈 커피 (Philz Coffee)", "디즈니랜드 리조트", "Roscoe's Chicken and Waffles",
        "샌디에이고 라호야 비치", "그리피스 천문대", "산타모니카 피어", "게티 센터",
        "페어몬트 샌프란시스코", "더 비벌리 힐스 호텔", "요세미티 밸리 롯지", "맨체스터 그랜드 하얏트 샌디에이고"
    ],
    "type": [
        "관광지", "맛집", "관광지", "맛집", "관광지", "맛집", "관광지", "관광지", "관광지", "관광지",
        "숙소", "숙소", "숙소", "숙소"
    ],
    "desc": [
        "세계에서 가장 아름다운 현수교 중 하나. 인생샷 명소📸",
        "캘리포니아의 국민버거! 비밀 메뉴 ‘애니멀 스타일’ 꼭 도전🍔",
        "대자연의 경이로움이 펼쳐지는 절경의 국립공원⛰️",
        "직접 블렌딩한 개성있는 커피☕ 로컬 감성 충만!",
        "꿈과 환상의 나라! 가족 단위 여행객에게 추천🎢",
        "프라이드 치킨 + 와플의 황홀한 조합🍗🧇",
        "바다사자도 구경하고, 에메랄드빛 바다에서 힐링🐬",
        "할리우드 사인을 볼 수 있는 최고의 뷰포인트. LA 야경 감상에 최고!🌃",
        "태평양의 아름다운 노을을 감상하며 즐길 수 있는 LA 대표 해변 유원지🎡",
        "웅장한 건축물과 세계적인 예술 작품들을 무료로 감상할 수 있는 곳🏛️",
        "샌프란시스코의 상징적인 럭셔리 호텔, 아름다운 도시 전망 제공🏨",
        "할리우드 스타들이 사랑하는 역사적인 럭셔리 호텔. 고급스러운 휴식을 즐겨보세요!✨",
        "요세미티 국립공원 내에 위치한 숙소로 주요 명소 접근성이 뛰어납니다🏕️",
        "샌디에이고 다운타운에 위치한 대형 호텔, 아름다운 베이 전망이 일품입니다🌊"
    ],
    "lat": [
        37.8199, 37.8080, 37.8651, 37.7749, 33.8121, 34.0900, 32.8500, 34.1185, 34.0089, 34.0781,
        37.7922, 34.0768, 37.7479, 32.7099
    ],
    "lon": [
        -122.4783, -122.4098, -119.5383, -122.4194, -117.9190, -118.3446, -117.2720, -118.3004, -118.4984, -118.4757,
        -122.4106, -118.4116, -119.6644, -117.1654
    ]
}
df = pd.DataFrame(locations_data)

st.markdown("---")

## 📍 어디로 떠나볼까요?

### 🗺️ 관광지, 맛집, 숙소 위치

# 사이드바 추가
st.sidebar.header("필터링 옵션")
# 사용자 입력: 지역 선택
city_options = ["전체"] + sorted(list(set(["샌프란시스코", "로스앤젤레스", "요세미티", "샌디에이고"])))
selected_city = st.sidebar.selectbox("도시 선택:", city_options)

# 사용자 입력: 카테고리 선택
type_options = ["전체"] + list(df["type"].unique())
selected_type = st.sidebar.selectbox("카테고리 선택:", type_options)

# 데이터 필터링
filtered_df = df.copy()
if selected_city != "전체":
    # 도시별 장소 분류 로직 업데이트 (숙소 포함)
    if selected_city == "샌프란시스코":
        filtered_df = filtered_df[(filtered_df["name"].isin(["샌프란시스코 금문교", "인앤아웃 버거 (In-N-Out)", "필즈 커피 (Philz Coffee)", "페어몬트 샌프란시스코"]))]
    elif selected_city == "로스앤젤레스":
        filtered_df = filtered_df[(filtered_df["name"].isin(["디즈니랜드 리조트", "Roscoe's Chicken and Waffles", "그리피스 천문대", "산타모니카 피어", "게티 센터", "더 비벌리 힐스 호텔"]))]
    elif selected_city == "요세미티":
        filtered_df = filtered_df[(filtered_df["name"].isin(["요세미티 국립공원", "요세미티 밸리 롯지"]))]
    elif selected_city == "샌디에이고":
        filtered_df = filtered_df[(filtered_df["name"].isin(["샌디에이고 라호야 비치", "맨체스터 그랜드 하얏트 샌디에이고"]))]

if selected_type != "전체":
    filtered_df = filtered_df[(filtered_df["type"] == selected_type)]

# 지도 초기화 (필터링된 데이터의 중앙을 기준으로)
if not filtered_df.empty:
    center_lat = filtered_df["lat"].mean()
    center_lon = filtered_df["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
else:
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6) # 캘리포니아 중앙

# 마커 추가
for idx, loc in filtered_df.iterrows():
    if loc["type"] == "관광지":
        icon_color = "blue"
    elif loc["type"] == "맛집":
        icon_color = "red"
    else: # 숙소
        icon_color = "green" # 숙소는 초록색으로 표시

    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=f"<b>{loc['name']}</b><br>{loc['desc']}",
        tooltip=loc["name"],
        icon=folium.Icon(color=icon_color)
    ).add_to(m)

st_data = st_folium(m, width=1000, height=600)

st.markdown("---")

## ✨ 세부 정보 및 추천

# 필터링된 결과 목록 출력
if not filtered_df.empty:
    st.markdown("### 📝 선택된 장소 목록:")
    for idx, row in filtered_df.iterrows():
        st.markdown(f"- **{row['name']}** ({row['type']}): {row['desc']}")
else:
    st.info("선택하신 조건에 해당하는 장소가 없습니다. 다른 필터를 시도해 보세요.")

st.markdown("---")

### 🚗 캘리포니아 교통 정보

st.markdown("캘리포니아는 넓은 지역에 다양한 볼거리가 흩어져 있어, 효율적인 교통 수단 선택이 중요합니다.")

st.subheader("🚘 렌터카")
st.markdown("자유로운 여행을 원한다면 렌터카가 가장 좋은 선택입니다. 하지만 대도시에서는 교통 체증과 주차 요금을 고려해야 합니다.")
st.markdown("[Google 지도에서 렌터카 검색하기](https://www.google.com/maps?q=렌터카)")

st.subheader("🚌 대중교통")
st.markdown("대도시(샌프란시스코, 로스앤젤레스, 샌디에이고)에서는 지하철, 버스 등 대중교통 시스템이 잘 갖춰져 있습니다. 하지만 도시 간 이동에는 불편할 수 있습니다.")
st.markdown("[Google 지도 대중교통 길찾기](https://www.google.com/maps?q=대중교통)")

st.subheader("✈️ 항공편")
st.markdown("도시 간 이동 시에는 항공편이 가장 빠르고 편리합니다. 캘리포니아 주요 도시에는 국제공항이 있습니다.")
st.markdown("[Google 항공편 검색](https://www.google.com/flights)")

st.subheader("🚆 기차")
st.markdown("암트랙(Amtrak) 기차를 이용하면 캘리포니아의 아름다운 풍경을 감상하며 이동할 수 있습니다. 하지만 시간이 오래 걸릴 수 있습니다.")
st.markdown("[암트랙(Amtrak) 웹사이트](https://www.amtrak.com/)")

st.markdown("---")

st.markdown("### ℹ️ Tip")
st.info("지도에서 마커를 클릭하면 설명이 나와요. 맛집은 **빨간색**, 관광지는 **파란색**, **숙소는 초록색**이에요. 왼쪽 사이드바에서 원하는 **도시**와 **카테고리**를 선택하여 맞춤 정보를 확인해 보세요!")
