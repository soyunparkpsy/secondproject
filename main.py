import streamlit as st
import folium
from streamlit_folium import st_folium

# 주요 관광지 및 맛집 정보
locations = [
    {
        "name": "San Francisco - Golden Gate Bridge",
        "description": "세계적으로 유명한 붉은 다리! 멋진 풍경과 사진 명소로 유명합니다.",
        "restaurant": "Tartine Bakery - 신선한 빵과 디저트가 일품!",
        "lat": 37.8199,
        "lon": -122.4783
    },
    {
        "name": "Los Angeles - Hollywood Sign",
        "description": "헐리우드의 상징적인 간판! 근처에는 전망 좋은 하이킹 코스도 있어요.",
        "restaurant": "In-N-Out Burger - 캘리포니아를 대표하는 수제버거 맛집!",
        "lat": 34.1341,
        "lon": -118.3215
    },
    {
        "name": "San Diego - La Jolla Cove",
        "description": "바다사자와 해양 생물을 가까이에서 볼 수 있는 아름다운 해변.",
        "restaurant": "George's at the Cove - 오션뷰와 신선한 해산물이 매력적인 고급 레스토랑.",
        "lat": 32.8503,
        "lon": -117.2720
    },
    {
        "name": "Yosemite National Park",
        "description": "대자연이 주는 경이로움! 폭포와 절벽, 하이킹 코스로 유명한 국립공원.",
        "restaurant": "The Ahwahnee Dining Room - 공원 내 최고급 다이닝 스팟!",
        "lat": 37.8651,
        "lon": -119.5383
    },
    {
        "name": "Santa Barbara",
        "description": "스페인풍 건축과 아름다운 해변이 어우러진 여유로운 도시.",
        "restaurant": "Brophy Bros - 항구 근처에서 먹는 신선한 해산물 요리.",
        "lat": 34.4208,
        "lon": -119.6982
    }
]

st.title("\U0001F5FA 캘리포니아 여행 가이드 ✨")
st.markdown("캘리포니아의 명소와 맛집 정보를 한눈에 확인해보세요!")

# 지도 생성
m = folium.Map(location=[36.7783, -119.4179], zoom_start=6)

# 마커 추가
for loc in locations:
    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=f"<b>{loc['name']}</b><br>{loc['description']}<br><i>맛집 추천: {loc['restaurant']}</i>",
        tooltip=loc["name"]
    ).add_to(m)

# 스트림릿에 지도 표시
st_data = st_folium(m, width=700, height=500)

# 관광지 리스트
st.subheader("\U0001F3D6 주요 명소 및 맛집 요약")
for loc in locations:
    st.markdown(f"### {loc['name']}")
    st.markdown(f"- 설명: {loc['description']}")
    st.markdown(f"- 맛집 추천: **{loc['restaurant']}**")
    st.markdown("---")
