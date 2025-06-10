import streamlit as st
import folium
from streamlit_folium import st_folium

# 앱 제목
st.title("🌴 캘리포니아 여행 & 맛집 가이드")
st.markdown("미국 캘리포니아의 주요 관광지와 그 근처의 맛집 정보를 지도와 함께 만나보세요! 🍔🌮🍷")

# 관광지 및 맛집 정보
locations = [
    {
        "name": "골든게이트 브릿지",
        "city": "샌프란시스코",
        "lat": 37.8199,
        "lon": -122.4783,
        "desc": "샌프란시스코의 상징인 붉은색 대교로, 멋진 전경과 사진 명소로 유명해요.",
        "food": ["Scoma’s – 해산물 레스토랑", "Boudin Bakery – 클램차우더로 유명한 빵집"]
    },
    {
        "name": "유니버설 스튜디오 할리우드",
        "city": "로스앤젤레스",
        "lat": 34.1381,
        "lon": -118.3534,
        "desc": "할리우드의 영화 세트장을 배경으로 한 테마파크로, 스릴 넘치는 놀이기구가 가득!",
        "food": ["In-N-Out Burger – 정통 캘리포니아 햄버거 체인", "NBC Sports Grill & Brew – 미국식 바비큐"]
    },
    {
        "name": "요세미티 국립공원",
        "city": "요세미티",
        "lat"
