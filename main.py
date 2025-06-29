import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd # 데이터 관리를 위해 pandas 추가

st.set_page_config(page_title="캘리포니아 관광 가이드", layout="wide")

st.title("🌴 캘리포니아 관광 & 맛집 가이드")
st.markdown("""
미국 서부의 보석, **캘리포니아** 🏄‍♀️  
관광명소부터 현지인 맛집까지, 이 가이드 하나면 여행 준비 끝!
""")

# 관광지와 맛집 데이터 (DataFrame으로 관리하여 유연성 확보)
locations_data = {
    "name": [
        "샌프란시스코 금문교", "인앤아웃 버거 (In-N-Out)", "요세미티 국립공원",
        "필즈 커피 (Philz Coffee)", "디즈니랜드 리조트", "Roscoe's Chicken and Waffles",
        "샌디에이고 라호야 비치", "그리피스 천문대", "산타모니카 피어", "게티 센터"
    ],
    "type": [
        "관광지", "맛집", "관광지", "맛집", "관광지", "맛집", "관광지", "관광지", "관광지", "관광지"
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
        "웅장한 건축물과 세계적인 예술 작품들을 무료로 감상할 수 있는 곳🏛️"
    ],
    "lat": [
        37.8199, 37.8080, 37.8651, 37.7749, 33.8121, 34.0900, 32.8500, 34.1185, 34.0089, 34.0781
    ],
    "lon": [
        -122.4783, -122.4098, -119.5383, -122.4194, -117.9190, -118.3446, -117.2720, -118.3004, -118.4984, -118.4757
    ]
}
df = pd.DataFrame(locations_data)

st.markdown("---")

## 📍 어디로 떠나볼까요?

### 🗺️ 관광지와 맛집 위치

# 사이드바 추가
st.sidebar.header("필터링 옵션")
# 사용자 입력: 지역 선택 (예시로 도시명 추가)
city_options = ["전체"] + sorted(list(set(["샌프란시스코", "로스앤젤레스", "요세미티", "샌디에이고"]))) # 도시 추가
selected_city = st.sidebar.selectbox("도시 선택:", city_options)

# 사용자 입력: 카테고리 선택
type_options = ["전체"] + list(df["type"].unique())
selected_type = st.sidebar.selectbox("카테고리 선택:", type_options)

# 데이터 필터링
filtered_df = df.copy()
if selected_city != "전체":
    if selected_city == "샌프란시스코":
        filtered_df = filtered_df[filtered_df["name"].isin(["샌프란시스코 금문교", "인앤아웃 버거 (In-N-Out)", "필즈 커피 (Philz Coffee)"])]
    elif selected_city == "로스앤젤레스":
        filtered_df = filtered_df[filtered_df["name"].isin(["디즈니랜드 리조트", "Roscoe's Chicken and Waffles", "그리피스 천문대", "산타모니카 피어", "게티 센터"])]
    elif selected_city == "요세미티":
        filtered_df = filtered_df[filtered_df["name"].isin(["요세미티 국립공원"])]
    elif selected_city == "샌디에이고":
        filtered_df = filtered_df[filtered_df["name"].isin(["샌디에이고 라호야 비치"])]

if selected_type != "전체":
    filtered_df = filtered_df[filtered_df["type"] == selected_type]

# 지도 초기화 (필터링된 데이터의 중앙을 기준으로)
if not filtered_df.empty:
    center_lat = filtered_df["lat"].mean()
    center_lon = filtered_df["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
else: # 필터링된 데이터가 없을 경우 기본값으로 초기화
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6)


# 마커 추가
for idx, loc in filtered_df.iterrows(): # DataFrame 반복 시 iterrows 사용
    icon_color = "blue" if loc["type"] == "관광지" else "red"
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

st.markdown("### ℹ️ Tip")
st.info("지도에서 마커를 클릭하면 설명이 나와요. 맛집은 **빨간색**, 관광지는 **파란색**이에요. 왼쪽 사이드바에서 원하는 **도시**와 **카테고리**를 선택하여 맞춤 정보를 확인해 보세요!")
