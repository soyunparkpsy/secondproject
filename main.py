import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 제목
st.title("🇪🇸 스페인 주요 관광지 가이드")
st.markdown("스페인의 대표적인 명소들을 한눈에 확인해보세요! 🧳✨")

# 주요 관광지 데이터
locations = [
    {
        "name": "마드리드 왕궁",
        "city": "마드리드",
        "lat": 40.417,
        "lon": -3.714,
        "desc": "유럽에서 가장 큰 왕궁 중 하나로, 웅장한 내부와 역사적인 전시물들을 감상할 수 있어요."
    },
    {
        "name": "사그라다 파밀리아",
        "city": "바르셀로나",
        "lat": 41.4036,
        "lon": 2.1744,
        "desc": "가우디의 대표 건축물로, 아직도 건설 중인 독특하고 아름다운 대성당입니다."
    },
    {
        "name": "알함브라 궁전",
        "city": "그라나다",
        "lat": 37.1761,
        "lon": -3.5881,
        "desc": "이슬람과 유럽 문화가 융합된 아름다운 궁전으로, 정원과 건축이 환상적입니다."
    },
    {
        "name": "세비야 대성당",
        "city": "세비야",
        "lat": 37.3861,
        "lon": -5.9921,
        "desc": "세계에서 세 번째로 큰 성당으로, 콜럼버스의 무덤이 이곳에 있어요."
    },
    {
        "name": "톨레도 구시가지",
        "city": "톨레도",
        "lat": 39.8628,
        "lon": -4.0273,
        "desc": "기독교, 이슬람, 유대교 문화가 공존했던 고도(古都)로, 중세 도시의 아름다움을 간직하고 있어요."
    }
]

# 지도 생성
spain_map = folium.Map(location=[40.0, -3.7], zoom_start=6)

# 마커 추가
for loc in locations:
    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=f"<b>{loc['name']}</b><br>{loc['desc']}",
        tooltip=loc["name"]
    ).add_to(spain_map)

# 지도 출력
st_folium(spain_map, width=700, height=500)

# 추가 설명
st.markdown("🗺️ 지도에 마커를 클릭하면 각 명소의 설명을 볼 수 있어요!")
st.markdown("💡 스페인은 지역마다 문화와 음식이 다양하니, 도시마다 새로운 경험을 즐겨보세요.")
