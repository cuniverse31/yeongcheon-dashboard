import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import json

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="영천시 취약지역 분석 대시보드", layout="wide")
st.markdown("<h2 style='text-align: center;'>🚨 영천시 복합 취약지역 마스터 대시보드</h2>", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 (캐싱) 및 상세 점수 계산
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('Yeongcheon_Dashboard_Final_Data.csv')
    gdf = gpd.read_file('Yeongcheon_Dashboard_Final_Data.geojson')
    
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
        
    # 🚨 [추가] 각 항목별 최종 기여 점수 계산 (위치 31.92% + 고령 42.68% + 식수 25.40%)
    # 지도 전체(GeoJSON)와 데이터프레임 툴팁에 표시하기 위한 파생 변수 생성
    df['점수_상세'] = df.apply(lambda x: f"{x['final_hybrid_score_100']:.1f} (위치 {x['norm_loc']*31.92:.1f} + 고령 {x['norm_pop']*42.68:.1f} + 식수 {x['norm_water']*25.40:.1f})", axis=1)
    gdf['점수_상세'] = gdf.apply(lambda x: f"{x['final_hybrid_score_100']:.1f} (위치 {x['norm_loc']*31.92:.1f} + 고령 {x['norm_pop']*42.68:.1f} + 식수 {x['norm_water']*25.40:.1f})", axis=1)
    
    with open('Yeongcheon_Top15_Report.json', 'r', encoding='utf-8') as f:
        top15_json = json.load(f)
    return df, gdf, top15_json

df, gdf, top15_json = load_data()

# ==========================================
# 3. 사이드바: AI 리포트 (사이드바는 깔끔하게 최종 점수만!)
# ==========================================
st.sidebar.header("🔥 집중 관리 타겟 Top 15")
st.sidebar.info("위치 취약도 하위 25% 제외 시나리오 반영")

for rank, item in enumerate(top15_json, 1):
    grid_id = item.get('격자코드', item.get('grid_id'))
    score = item.get('final_hybrid_score_100', 0)
    report = item.get('Final_Dashboard_Report', '리포트가 존재하지 않습니다.')
    
    # 🚨 [수정] 사이드바 제목은 예전처럼 깔끔하게 최종 점수만 표시
    with st.sidebar.expander(f"Top {rank} | {grid_id} ({score:.1f}점)"):
        st.markdown(f"""
        <div style="line-height: 1.6; word-break: keep-all; font-size: 0.9rem; background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 5px solid #e74c3c;">
            <b>🤖 AI 심층 리포트</b><br>
            {report}
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 레이어 선택 및 컬러 설정
# ==========================================
layer_options = {
    "🔥 종합 취약도 (순위 마커 표시)": "final_hybrid_score_100",
    "🌟 AI 군집화 분류 (K=5)": "군집_유형",
    "💧 식수 환경 취약도": "norm_water",
    "👵 고령 인구 취약도": "norm_pop",
    "🚑 위치 인프라 취약도": "norm_loc"
}
selected_name = st.radio("시각화할 지표를 선택하세요:", list(layer_options.keys()), horizontal=True)
selected_col = layer_options[selected_name]

# --- 컬러맵 설정 ---
target_only_gdf = gdf[gdf['is_safe_zone'] == False]

if selected_col == "final_hybrid_score_100":
    # 종합 취약도용 진한 컬러
    colormap = cm.LinearColormap(colors=['#ffeda0', '#feb24c', '#f03b20'], 
                                 vmin=target_only_gdf['final_hybrid_score_100'].min(), 
                                 vmax=target_only_gdf['final_hybrid_score_100'].max())
    cluster_colors = {}
else:
    # 나머지 지표용 예전의 연한 컬러/오리지널 설정
    colors_map = {
        "norm_water": ['#f7fbff', '#6baed6', '#08306b'],
        "norm_pop": ['#fff5eb', '#fd8d3c', '#7f2704'],
        "norm_loc": ['#fcfbfd', '#9e9ac8', '#3f007d']
    }
    if selected_col in colors_map:
        colormap = cm.LinearColormap(colors=colors_map[selected_col], vmin=0, vmax=1)
    else: colormap = None

    # AI 군집용 오리지널 색상
    cluster_colors = {
        "초고령·식수 복합 위기 구역 (긴급 구호 최우선)": "#e74c3c", 
        "고령화 집중 취약 구역 (노인 복지/돌봄 필요)": "#f39c12", 
        "교통/의료 고립 구역 (물리적 이동권 보장 필요)": "#2ecc71", 
        "식수 환경 취약 구역 (상수도 보급 시급)": "#3498db",      
        "기초 인프라 양호 구역 (정책 후순위)": "#bdc3c7"         
    }

# 지도 초기화
center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
m = folium.Map(location=center, zoom_start=11, tiles="CartoDB positron")

# ==========================================
# 5. 별표 순위 마커 및 상세 툴팁 (Top 15)
# ==========================================
if selected_col == "final_hybrid_score_100":
    top15_gdf = target_only_gdf.sort_values(by='final_hybrid_score_100', ascending=False).head(15)
    for rank, row in enumerate(top15_gdf.itertuples(), 1):
        m_lat = row.geometry.centroid.y
        m_lon = row.geometry.centroid.x
        
        icon_html = f'''
        <div style="position: relative; text-align: center; width: 40px;">
            <span style="color: gold; font-size: 30pt; text-shadow: 1px 1px 2px #000;">★</span>
            <span style="position: absolute; top: 52%; left: 50%; transform: translate(-50%, -50%); 
                         color: black; font-weight: bold; font-size: 9pt;">{rank}</span>
        </div>
        '''
        # 지도 툴팁에는 상세 점수(가중치) 표시 유지
        detailed_tooltip = f"""
        <div style="font-family: sans-serif; padding: 5px; line-height: 1.4;">
            <b style="color: #e74c3c;">🏆 위기 순위: {rank}위</b><br>
            <b>격자코드:</b> {row.격자코드}<br>
            <b>카테고리:</b> {row.군집_유형}<br>
            <b style="color: #BD0026;">종합점수: {row.점수_상세}</b>
        </div>
        """
        folium.Marker(
            location=[m_lat, m_lon],
            icon=folium.features.DivIcon(html=icon_html, icon_anchor=(20, 20)),
            tooltip=folium.Tooltip(detailed_tooltip)
        ).add_to(m)

# ==========================================
# 6. 범례 및 레이어 스타일링
# ==========================================
if selected_col == "군집_유형":
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 250px; height: 160px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:13px;
                padding: 10px; border-radius: 10px; opacity: 0.9; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
    <b style="font-size:14px;">📍 AI 군집 유형 분류</b><hr style="margin:5px 0;">
    <i style="background:#e74c3c;width:12px;height:12px;display:inline-block;margin-right:5px;border:1px solid #000;"></i>초고령·식수 복합 위기 (우선)<br>
    <i style="background:#f39c12;width:12px;height:12px;display:inline-block;margin-right:5px;border:1px solid #000;"></i>고령화 집중 취약 구역<br>
    <i style="background:#2ecc71;width:12px;height:12px;display:inline-block;margin-right:5px;border:1px solid #000;"></i>교통/의료 고립 구역<br>
    <i style="background:#3498db;width:12px;height:12px;display:inline-block;margin-right:5px;border:1px solid #000;"></i>식수 환경 취약 구역<br>
    <i style="background:#bdc3c7;width:12px;height:12px;display:inline-block;margin-right:5px;border:1px solid #000;"></i>기초 인프라 양호 (Safe Zone)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

def style_fn(feature):
    props = feature['properties']
    is_safe = props.get('is_safe_zone', False)
    
    if selected_col == "final_hybrid_score_100":
        if is_safe:
            fill = "#2ecc71" 
            opacity = 0.4
        else:
            fill = colormap(props[selected_col])
            opacity = 0.9
    else:
        if selected_col == "군집_유형":
            fill = cluster_colors.get(props['군집_유형'], "#808080")
        else:
            fill = colormap(props[selected_col])
        opacity = 0.7 
        
    return {
        'fillColor': fill, 
        'color': 'black', 
        'weight': 0.3, 
        'fillOpacity': opacity
    }

# 지도 전체 호버 시 툴팁에도 '점수_상세' 표시 유지
folium.GeoJson(
    gdf, 
    style_function=style_fn, 
    tooltip=folium.GeoJsonTooltip(fields=['격자코드', '군집_유형', '점수_상세'], aliases=['격자:', '유형:', '점수 상세:'])
).add_to(m)

if colormap: m.add_child(colormap)

# 지도 출력
st_folium(m, width=1200, height=750)

# 7. 데이터 테이블
with st.expander("📝 전체 분석 데이터 상세보기"):
    show_df = df.sort_values(by='final_hybrid_score_100', ascending=False)
    cols = ['격자코드', '점수_상세', '군집_유형'] + [c for c in show_df.columns if c not in ['격자코드', '점수_상세', '군집_유형']]
    st.dataframe(show_df[cols])