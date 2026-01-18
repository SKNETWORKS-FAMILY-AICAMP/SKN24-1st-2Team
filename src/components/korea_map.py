import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from pathlib import Path

# ========== GeoJSON 캐시 경로 ==========
GEOJSON_CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "geojson"
GEOJSON_CACHE_FILE = GEOJSON_CACHE_DIR / "korea_provinces_simplified.json"
GEOJSON_PROVINCES_BOUNDARY_CACHE_FILE = GEOJSON_CACHE_DIR / "korea_provinces_boundaries_simplified.json"

# 디테일 조절
OUTLINE_MAX_POINTS = 260
PROVINCE_MAX_POINTS = 90


# ========== GeoJSON 단순화 함수 ==========
def _simplify_coordinates(coords, max_points=15):
    if len(coords) <= max_points:
        return coords
    
    step = max(1, len(coords) // max_points)
    simplified = coords[::step]
    
    if simplified[0] != simplified[-1]:
        simplified.append(simplified[0])
    
    return simplified


def _simplify_geojson(geojson):
    simplified = {
        "type": geojson["type"],
        "features": []
    }
    
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        
        if geom_type == "Polygon":
            simplified_coords = [_simplify_coordinates(ring, max_points=15) for ring in coords]
        elif geom_type == "MultiPolygon":
            simplified_coords = [
                [_simplify_coordinates(ring, max_points=15) for ring in polygon]
                for polygon in coords
            ]
        else:
            simplified_coords = coords
        
        simplified["features"].append({
            "type": "Feature",
            "properties": feature["properties"],
            "geometry": {"type": geom_type, "coordinates": simplified_coords}
        })
    
    return simplified


# ========== GeoJSON 로드 ==========
@st.cache_data(ttl=86400)
def load_korea_geojson():
    if GEOJSON_CACHE_FILE.exists():
        with open(GEOJSON_CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
            if "features" in cached and len(cached["features"]) == 1:
                return cached
    
    # 캐시된 파일 없을 시 다운로드
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json"
    response = requests.get(url, timeout=10)
    geojson = response.json()
    
    # 시도 통합
    all_exterior_coords = []
    
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        
        if geom_type == "Polygon":
            if coords and len(coords) > 0:
                all_exterior_coords.append(coords[0])
        elif geom_type == "MultiPolygon":
            for polygon in coords:
                if polygon and len(polygon) > 0:
                    all_exterior_coords.append(polygon[0])
    
    if all_exterior_coords:
        main_outline = max(all_exterior_coords, key=len)
        simplified_outline = _simplify_coordinates(main_outline, max_points=OUTLINE_MAX_POINTS)
        
        merged_geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"name": "South Korea"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [simplified_outline]
                }
            }]
        }
    else:
        merged_geojson = _simplify_geojson(geojson)
    
    GEOJSON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(GEOJSON_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_geojson, f, ensure_ascii=False)
    
    return merged_geojson


@st.cache_data(ttl=86400)
def load_korea_provinces_geojson():
    if GEOJSON_PROVINCES_BOUNDARY_CACHE_FILE.exists():
        with open(GEOJSON_PROVINCES_BOUNDARY_CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
            meta = cached.get("_meta", {})
            if (
                "features" in cached
                and len(cached["features"]) >= 8
                and meta.get("province_max_points") == PROVINCE_MAX_POINTS
            ):
                return cached

    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json"
    response = requests.get(url, timeout=10)
    geojson = response.json()

    # 좌표 단순화
    simplified = {
        "type": geojson.get("type", "FeatureCollection"),
        "_meta": {"province_max_points": PROVINCE_MAX_POINTS},
        "features": [],
    }

    for idx, feature in enumerate(geojson.get("features", [])):
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")

        if not coords:
            continue

        if geom_type == "Polygon":
            simplified_coords = [_simplify_coordinates(ring, max_points=PROVINCE_MAX_POINTS) for ring in coords]
        elif geom_type == "MultiPolygon":
            simplified_coords = [
                [_simplify_coordinates(ring, max_points=PROVINCE_MAX_POINTS) for ring in polygon]
                for polygon in coords
            ]
        else:
            simplified_coords = coords

        props = dict(feature.get("properties", {}) or {})
        # Choropleth용 feature id
        props["_fid"] = idx

        simplified["features"].append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {"type": geom_type, "coordinates": simplified_coords},
            }
        )

    GEOJSON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(GEOJSON_PROVINCES_BOUNDARY_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False)

    return simplified


def _build_boundary_lines_from_geojson(geojson):
    """
    GeoJSON(Polygon/MultiPolygon)에서 경계선 라인용 lat/lon 배열 생성
    - Plotly에서 라인 분리하려면 None separator 사용
    """
    lons = []
    lats = []

    for feature in geojson.get("features", []):
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates") or []

        def add_ring(ring):
            # ring: [[lon, lat], ...]
            for pt in ring:
                if not pt or len(pt) < 2:
                    continue
                lon, lat = pt[0], pt[1]
                lons.append(lon)
                lats.append(lat)
            lons.append(None)
            lats.append(None)

        if geom_type == "Polygon":
            if len(coords) > 0:
                add_ring(coords[0])  # 외곽선만
        elif geom_type == "MultiPolygon":
            for polygon in coords:
                if polygon and len(polygon) > 0:
                    add_ring(polygon[0])  # 각 폴리곤 외곽선만

    return lons, lats


# ========== 지도 렌더링 ==========
@st.cache_data
def create_bubble_map(df_json, filter_type = "charging", lightweight = False, _version = 5):
    """
    팔도 단위 버블 지도 생성 (캐싱 지원)
    - 단순한 경계선만 있는 배경 + 버블 표시
    """
    # JSON에서 DataFrame 복원
    df = pd.read_json(df_json)
    
    # 팔도(시도) GeoJSON 로드
    provinces_geojson = load_korea_provinces_geojson()
    
    # 버블 크기 계산
    if filter_type == "charging":
        sizeref = 2.0 * max(df["count"]) / (80 ** 2)
        text_values = [f"{region}<br>{v:,}" for region, v in zip(df["region"], df["count"])]
        hover_template = "<b>%{customdata[0]}</b><br>충전소: %{customdata[1]:,}기<extra></extra>"
    else:
        sizeref = 2.0 * max(df["count"]) / (70 ** 2)
        text_values = [f"{region}<br>{v:.1f}%" for region, v in zip(df["region"], df["count"])]
        hover_template = "<b>%{customdata[0]}</b><br>전기 화물차 비중: %{customdata[1]:.1f}%<extra></extra>"
    
    # Figure 생성
    fig = go.Figure()
    
    province_ids = [f.get("properties", {}).get("_fid") for f in provinces_geojson.get("features", [])]
    province_ids = [pid for pid in province_ids if pid is not None]
    fig.add_trace(go.Choropleth(
        geojson=provinces_geojson,
        locations=province_ids,
        z=[1] * len(province_ids),
        featureidkey="properties._fid",
        colorscale=[
            [0, "rgba(0, 0, 0, 0)"],
            [1, "rgba(55, 65, 81, 0.55)"],
        ],
        marker_line_width=1.2,
        marker_line_color="rgba(255, 255, 255, 0.10)",
        showscale=False,
        hoverinfo="skip",
    ))

    boundary_lons, boundary_lats = _build_boundary_lines_from_geojson(provinces_geojson)
    fig.add_trace(go.Scattergeo(
        lon=boundary_lons,
        lat=boundary_lats,
        mode="lines",
        line=dict(
            color="rgba(255, 255, 255, 0.10)",  # 아주 연한 경계선
            width=1,
        ),
        hoverinfo="skip",
        name="",
    ))
    
    border_width = 2 if not lightweight else 1
    fig.add_trace(go.Scattergeo(
        lat=df["lat"],
        lon=df["lon"],
        mode="markers",
        marker=dict(
            size=df["count"],
            sizemode="area",
            sizeref=sizeref,
            sizemin=35,
            color="rgba(59, 130, 246, 0.98)",
            line=dict(
                color="rgba(191, 219, 254, 0.90)",
                width=border_width,
            ),
            opacity=1,
        ),
        customdata=list(zip(df["region"], df["count"])),
        hovertemplate=hover_template,
        name="",
    ))
    
    fig.add_trace(go.Scattergeo(
        lat=df["lat"],
        lon=df["lon"],
        mode="text",
        text=text_values,
        textfont=dict(
            size=12,
            color="white",
            family="Pretendard, -apple-system, sans-serif",
        ),
        textposition="middle center",
        hoverinfo="skip",
        name="",
    ))
    
    # 레이아웃
    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        geo=dict(
            projection=dict(type="mercator"),
            center=dict(lat=36.0, lon=127.5),
            lataxis=dict(range=[33.0, 39.8]),
            lonaxis=dict(range=[124.3, 131.9]),
            bgcolor="rgba(10, 10, 10, 0)",  # CSS 배경 사용
            showframe=False,
            showcoastlines=False,
            showcountries=False,
            showland=False,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=550,
    )
    
    return fig


def render_map_section(df, filter_type = "charging", lightweight = True):
    """
    지도 섹션 렌더링
    """
    # df -> json
    df_json = df.to_json()
    
    fig = create_bubble_map(df_json, filter_type, lightweight, _version=3)
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,  # 툴바 숨김
            "scrollZoom": True,  # 스크롤 줌 활성화
        }
    )


