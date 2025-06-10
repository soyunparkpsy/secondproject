import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="centered", page_title="광합성량 시뮬레이션")

def calculate_photosynthesis(light_intensity, temperature, co2_concentration):
    """
    주어진 환경 요인에 따른 광합성량을 계산합니다.
    이 모델은 단순화된 시뮬레이션이며, 실제 생물학적 과정과 정확히 일치하지 않을 수 있습니다.
    """
    # 각 요인이 광합성에 미치는 영향 (예시 값)
    # 실제 생물학적 모델은 훨씬 복잡합니다.

    # 빛의 세기 영향: 특정 세기까지는 증가하다가 포화
    light_effect = 1 - np.exp(-0.05 * light_intensity)

    # 온도 영향: 최적 온도(예: 25도)에서 최고, 너무 높거나 낮으면 감소
    optimal_temp = 25
    temp_effect = np.exp(-0.01 * (temperature - optimal_temp)**2)

    # 이산화 탄소 농도 영향: 특정 농도까지는 증가하다가 포화
    co2_effect = 1 - np.exp(-0.02 * co2_concentration)

    # 모든 요인의 곱으로 광합성량 결정 (단순화된 모델)
    photosynthesis_rate = 100 * light_effect * temp_effect * co2_effect
    return photosynthesis_rate

st.title("🌱 환경 요인에 따른 광합성량 시뮬레이션")

st.markdown("""
이 앱은 **빛의 세기**, **온도**, **이산화 탄소의 농도**가 식물의 광합성량에 어떻게 영향을 미치는지 시뮬레이션합니다.
아래 슬라이더를 조절하여 각 환경 요인을 변경하고, 그에 따른 광합성량 변화를 그래프로 확인해보세요.
""")

st.markdown("---")

## 환경 요인 조절 및 개별 그래프

# 각 슬라이더의 기본값을 미리 설정하여 그래프 계산에 사용
# 이는 스트림릿이 위에서 아래로 실행되면서 변수가 정의되지 않았을 때의 오류를 방지합니다.
# 사용자가 슬라이더를 조절하면 해당 값이 업데이트되고 앱이 다시 실행됩니다.
default_light = 500
default_temp = 25
default_co2 = 400

# 1. 빛의 세기 조절 및 그래프
st.markdown("### 💡 빛의 세기")
light_intensity = st.slider(
    "빛의 세기 (lux)",
    min_value=0,
    max_value=1000,
    value=default_light, # 초기값 설정
    step=10,
    key="light_slider",
    help="빛의 세기가 강할수록 광합성량이 증가하지만, 일정 수준 이상에서는 포화됩니다."
)

# 빛의 세기 변화에 따른 광합성량 그래프
fig_light, ax_light = plt.subplots(figsize=(10, 4))
light_values = np.linspace(0, 1000, 100)
# 현재 light_intensity는 슬라이더 값, temperature와 co2_concentration은 기본값 또는 다른 슬라이더의 현재 값을 사용
photosynthesis_vs_light = [calculate_photosynthesis(l, default_temp, default_co2) for l in light_values]
ax_light.plot(light_values, photosynthesis_vs_light, color='orange')
ax_light.axvline(x=light_intensity, color='r', linestyle='--', label=f'현재 설정: {light_intensity} lux')
ax_light.set_title(f"빛의 세기에 따른 광합성량 (온도: {default_temp}°C, CO2: {default_co2} ppm 고정)")
ax_light.set_xlabel("빛의 세기 (lux)")
ax_light.set_ylabel("광합성량")
ax_light.grid(True)
ax_light.legend()
st.pyplot(fig_light)
plt.close(fig_light) # 메모리 해제

st.markdown("---")

# 2. 온도 조절 및 그래프
st.markdown("### 🌡️ 온도")
temperature = st.slider(
    "온도 (°C)",
    min_value=0,
    max_value=40,
    value=default_temp, # 초기값 설정
    step=1,
    key="temp_slider",
    help="광합성은 최적의 온도에서 가장 활발하며, 너무 낮거나 높으면 감소합니다."
)

# 온도 변화에 따른 광합성량 그래프
fig_temp, ax_temp = plt.subplots(figsize=(10, 4))
temp_values = np.linspace(0, 40, 100)
# 현재 temperature는 슬라이더 값, light_intensity와 co2_concentration은 기본값 또는 다른 슬라이더의 현재 값을 사용
photosynthesis_vs_temp = [calculate_photosynthesis(default_light, t, default_co2) for t in temp_values]
ax_temp.plot(temp_values, photosynthesis_vs_temp, color='red')
ax_temp.axvline(x=temperature, color='r', linestyle='--', label=f'현재 설정: {temperature} °C')
ax_temp.set_title(f"온도에 따른 광합성량 (빛: {default_light} lux, CO2: {default_co2} ppm 고정)")
ax_temp.set_xlabel("온도 (°C)")
ax_temp.set_ylabel("광합성량")
ax_temp.grid(True)
ax_temp.legend()
st.pyplot(fig_temp)
plt.close(fig_temp) # 메모리 해제

st.markdown("---")

# 3. 이산화 탄소 농도 조절 및 그래프
st.markdown("### 💨 이산화 탄소 농도")
co2_concentration = st.slider(
    "이산화 탄소 농도 (ppm)",
    min_value=0,
    max_value=1000,
    value=default_co2, # 초기값 설정
    step=10,
    key="co2_slider",
    help="이산화 탄소 농도가 높을수록 광합성량이 증가하지만, 일정 수준 이상에서는 포화됩니다."
)

# CO2 농도 변화에 따른 광합성량 그래프
fig_co2, ax_co2 = plt.subplots(figsize=(10, 4))
co2_values = np.linspace(0, 1000, 100)
# 현재 co2_concentration은 슬라이더 값, light_intensity와 temperature는 기본값 또는 다른 슬라이더의 현재 값을 사용
photosynthesis_vs_co2 = [calculate_photosynthesis(default_light, default_temp, c) for c in co2_values]
ax_co2.plot(co2_values, photosynthesis_vs_co2, color='green')
ax_co2.axvline(x=co2_concentration, color='r', linestyle='--', label=f'현재 설정: {co2_concentration} ppm')
ax_co2.set_title(f"이산화 탄소 농도에 따른 광합성량 (빛: {default_light} lux, 온도: {default_temp}°C 고정)")
ax_co2.set_xlabel("이산화 탄소 농도 (ppm)")
ax_co2.set_ylabel("광합성량")
ax_co2.grid(True)
ax_co2.legend()
st.pyplot(fig_co2)
plt.close(fig_co2) # 메모리 해제

st.markdown("---")

# 현재 설정된 모든 환경 요인으로 최종 광합성량 계산 및 표시
final_photosynthesis = calculate_photosynthesis(light_intensity, temperature, co2_concentration)
st.subheader(f"✅ 현재 설정된 모든 환경 요인으로 계산된 총 광합성량: **{final_photosynthesis:.2f}** 단위")

st.markdown("---")
st.info("이 시뮬레이션은 광합성 원리를 이해하기 위한 **매우 단순화된 모델**입니다. 실제 식물의 광합성은 훨씬 더 복잡하며, 다양한 생화학적 과정과 환경 요인들이 상호작용합니다.")
st.markdown("궁금한 점이 있으시면 언제든지 질문해주세요!")
