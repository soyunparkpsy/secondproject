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

## 환경 요인 조절

# 슬라이더를 사용하여 각 환경 요인 조절
light_intensity = st.slider(
    "💡 빛의 세기 (lux)",
    min_value=0,
    max_value=1000,
    value=500,
    step=10,
    help="빛의 세기가 강할수록 광합성량이 증가하지만, 일정 수준 이상에서는 포화됩니다."
)

temperature = st.slider(
    "🌡️ 온도 (°C)",
    min_value=0,
    max_value=40,
    value=25,
    step=1,
    help="광합성은 최적의 온도에서 가장 활발하며, 너무 낮거나 높으면 감소합니다."
)

co2_concentration = st.slider(
    "💨 이산화 탄소 농도 (ppm)",
    min_value=0,
    max_value=1000,
    value=400,
    step=10,
    help="이산화 탄소 농도가 높을수록 광합성량이 증가하지만, 일정 수준 이상에서는 포화됩니다."
)

st.markdown("---")

## 광합성량 결과

# 현재 설정된 환경 요인으로 광합성량 계산
current_photosynthesis = calculate_photosynthesis(light_intensity, temperature, co2_concentration)

st.subheader(f"현재 광합성량: **{current_photosynthesis:.2f}** 단위")

# 광합성량 그래프 그리기
st.subheader("환경 요인 변화에 따른 광합성량 그래프")

# 각 요인별 광합성량 변화 시뮬레이션
# 빛의 세기 변화에 따른 광합성량
light_values = np.linspace(0, 1000, 100)
photosynthesis_vs_light = [calculate_photosynthesis(l, temperature, co2_concentration) for l in light_values]

# 온도 변화에 따른 광합성량
temp_values = np.linspace(0, 40, 100)
photosynthesis_vs_temp = [calculate_photosynthesis(light_intensity, t, co2_concentration) for t in temp_values]

# CO2 농도 변화에 따른 광합성량
co2_values = np.linspace(0, 1000, 100)
photosynthesis_vs_co2 = [calculate_photosynthesis(light_intensity, temperature, c) for c in co2_values]

fig, ax = plt.subplots(3, 1, figsize=(10, 15))
fig.suptitle("각 환경 요인 변화에 따른 광합성량 (다른 요인 고정)", fontsize=16)

# 빛의 세기 그래프
ax[0].plot(light_values, photosynthesis_vs_light, color='orange')
ax[0].axvline(x=light_intensity, color='r', linestyle='--', label=f'현재 빛: {light_intensity} lux')
ax[0].set_title("빛의 세기에 따른 광합성량")
ax[0].set_xlabel("빛의 세기 (lux)")
ax[0].set_ylabel("광합성량")
ax[0].grid(True)
ax[0].legend()

# 온도 그래프
ax[1].plot(temp_values, photosynthesis_vs_temp, color='red')
ax[1].axvline(x=temperature, color='r', linestyle='--', label=f'현재 온도: {temperature} °C')
ax[1].set_title("온도에 따른 광합성량")
ax[1].set_xlabel("온도 (°C)")
ax[1].set_ylabel("광합성량")
ax[1].grid(True)
ax[1].legend()

# CO2 농도 그래프
ax[2].plot(co2_values, photosynthesis_vs_co2, color='green')
ax[2].axvline(x=co2_concentration, color='r', linestyle='--', label=f'현재 CO2: {co2_concentration} ppm')
ax[2].set_title("이산화 탄소 농도에 따른 광합성량")
ax[2].set_xlabel("이산화 탄소 농도 (ppm)")
ax[2].set_ylabel("광합성량")
ax[2].grid(True)
ax[2].legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # 전체 레이아웃 조정
st.pyplot(fig)

st.markdown("---")
st.info("이 시뮬레이션은 광합성 원리를 이해하기 위한 **매우 단순화된 모델**입니다. 실제 식물의 광합성은 훨씬 더 복잡하며, 다양한 생화학적 과정과 환경 요인들이 상호작용합니다.")

st.markdown("궁금한 점이 있으시면 언제든지 질문해주세요!")
