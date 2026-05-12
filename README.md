# yeongcheon-dashboard

# 🚨 영천시 복합 취약지역 마스터 대시보드

**데이터 시각화 공모전 출품작 | Team 영천의미학**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yeongcheon-dashboard.streamlit.app/) 
*(👆 위 배너를 클릭하면 대시보드 웹사이트로 바로 이동합니다!)*

---

## 📌 프로젝트 개요
지방 소도시의 초고령화와 인구 소멸 이슈에 대응하기 위해, 영천시 전역을 **1km 격자(Grid)** 단위로 분할하여 생활·안전 복합 사각지대를 정밀 타겟팅한 인터랙티브 대시보드입니다. 

일률적인 복지 예산 투입의 한계를 극복하고자 **'하이브리드 가중치'** 모델을 개발하고, **기계학습(K-Means)** 알고리즘을 통해 취약 지역을 5대 정책 타겟군으로 유형화(Typology)하였습니다.

## 💡 핵심 기능
* **하이브리드 가중치 산출:** 객관적 통계(Entropy) + 데이터 신뢰도(Reliability) + 전문가 직관(AHP)을 융합한 정교한 취약 점수 산출
* **5대 정책 타겟군 도출 (K=5):** 단순 점수 나열이 아닌, 초고령·식수 복합 위기, 교통/의료 고립 등 맞춤형 행정 처방이 가능한 군집화 모델링
* **인터랙티브 웹 대시보드:** Folium 기반의 동적 지도 시각화 및 직관적인 UI/UX 구현
* **AI 행정 심층 리포트:** OpenAI API를 활용하여 도출된 격자별 데이터(Top 15)를 기반으로, 공공 행정 문법에 맞춘 즉각적인 대응 전략 리포트 제공

## 🛠️ Tech Stack
* **Language:** Python
* **Data & Spatial Analysis:** Pandas, GeoPandas
* **Visualization:** Folium, Branca Colormap
* **Web Framework & AI:** Streamlit, OpenAI (gpt-4o-mini)

---
*본 프로젝트는 데이터 기반의 의사결정을 지원하여, 지자체의 행정 대응력을 극대화하는 '지방 소도시형 복지 표준 모델'을 제안합니다.*
