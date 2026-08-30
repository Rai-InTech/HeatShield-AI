import time
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from shapely.geometry import shape
from streamlit_folium import st_folium

# ============================================================
# HEATSHIELD AI — Streamlit wrapper around the notebook logic
# ============================================================

st.set_page_config(
    page_title="HeatShield AI",
    page_icon="🔥",
    layout="wide",
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px;}
.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
    border: 1px solid #fed7aa;
    margin-bottom: 1rem;
}
.hero h1 {margin: 0 0 .25rem 0; font-size: 2.3rem;}
.hero p {margin: 0; color: #57534e; font-size: 1.05rem;}
.kpi {
    padding: 1rem;
    border: 1px solid #e7e5e4;
    border-radius: 14px;
    background: white;
    min-height: 105px;
}
.kpi-label {font-size: .85rem; color: #78716c; margin-bottom: .3rem;}
.kpi-value {font-size: 1.65rem; font-weight: 700;}
.small-note {color:#78716c; font-size:.82rem;}
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://api.fortyguard.com/v1"

RISK_COLORS = {
    "CRITICAL": "#d73027",
    "HIGH": "#fc8d59",
    "MODERATE": "#fee08b",
    "LOW": "#91cf60",
}

def get_api_key():
    try:
        return st.secrets["FORTYGUARD_API_KEY"]
    except Exception:
        return None

def submit_heatmap(api_key, aoi, date, time_str, granularity=100):
    """Same FortyGuard heatmap submission flow used in HEATSHIELD.ipynb."""
    url = f"{BASE_URL}/heatmap"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "polygon_aoi": aoi,
        "date_time": {
            "start_date": date,
            "start_time": time_str,
            "filter_type": 1,
        },
        "granularity": granularity,
    }

    response = requests.post(
        url, headers=headers, json=payload, timeout=60
    )
    response.raise_for_status()
    result = response.json()

    return result["data"]["activity_id"]

def wait_for_activity(api_key, activity_id, max_wait=600, interval=5):
    """Same polling flow used in the notebook."""
    status_url = f"{BASE_URL}/status/{activity_id}"
    start = time.time()

    while True:
        response = requests.get(
            status_url,
            headers={"api-key": api_key},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()["data"]
        status = data.get("status")

        if status == "Completed":
            return data

        if status == "Failed":
            raise RuntimeError(f"FortyGuard activity failed: {activity_id}")

        if time.time() - start > max_wait:
            raise TimeoutError("FortyGuard activity exceeded maximum wait time.")

        time.sleep(interval)

def build_risk_engine(map_data):
    """Notebook risk engine: normalization + persistence + exceedance + weighted risk."""
    features = map_data.get("features", [])
    records = []

    for feature in features:
        properties = feature.get("properties", {})
        geometry = shape(feature["geometry"])
        records.append({"geometry": geometry, **properties})

    heat_gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")

    temp_col = "average_temperature"
    heat_gdf[temp_col] = pd.to_numeric(
        heat_gdf[temp_col], errors="coerce"
    )
    heat_gdf = heat_gdf.dropna(subset=[temp_col]).copy()

    # Temperature normalization — directly from the notebook.
    t_min = heat_gdf[temp_col].min()
    t_max = heat_gdf[temp_col].max()

    if t_max == t_min:
        heat_gdf["temperature_score"] = 0.0
    else:
        heat_gdf["temperature_score"] = (
            (heat_gdf[temp_col] - t_min) / (t_max - t_min) * 100
        )

    # Spatial snapshot baseline — directly from the notebook.
    heat_gdf["persistence_score"] = 50.0

    # Exceedance — directly from the notebook.
    HEAT_THRESHOLD = 32.0
    heat_gdf["exceedance_score"] = np.clip(
        (heat_gdf[temp_col] - HEAT_THRESHOLD) / 8.0 * 100,
        0,
        100,
    )

    # Final weighted risk — directly from the notebook.
    heat_gdf["risk_score"] = (
        heat_gdf["temperature_score"] * 0.60
        + heat_gdf["persistence_score"] * 0.25
        + heat_gdf["exceedance_score"] * 0.15
    )
    heat_gdf["risk_score"] = heat_gdf["risk_score"].clip(0, 100)

    def classify_heat(score):
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MODERATE"
        else:
            return "LOW"

    heat_gdf["risk_level"] = heat_gdf["risk_score"].apply(classify_heat)

    def recommend_intervention(row):
        score = row["risk_score"]
        if score >= 80:
            return "Priority cooling + shade + trees + cool surfaces"
        elif score >= 60:
            return "Shade infrastructure + tree canopy"
        elif score >= 40:
            return "Increase vegetation + reflective surfaces"
        else:
            return "Maintain existing cooling infrastructure"

    heat_gdf["recommendation"] = heat_gdf.apply(
        recommend_intervention, axis=1
    )

    return heat_gdf

def make_map(heat_gdf):
    """Notebook Folium map, adapted only for Streamlit rendering."""
    heat_map_gdf = heat_gdf.to_crs(epsg=4326)

    m = folium.Map(
        location=[37.3382, -121.8863],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    def style_feature(feature):
        level = feature["properties"].get("risk_level", "LOW")
        return {
            "fillColor": RISK_COLORS.get(level, "#91cf60"),
            "color": "#333333",
            "weight": 0.5,
            "fillOpacity": 0.65,
        }

    folium.GeoJson(
        heat_map_gdf.to_json(),
        name="Heat Risk Zones",
        style_function=style_feature,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "tile_id",
                "average_temperature",
                "risk_score",
                "risk_level",
                "recommendation",
            ],
            aliases=[
                "Tile",
                "Temperature °C",
                "Risk Score",
                "Risk Level",
                "Recommendation",
            ],
            localize=True,
            sticky=False,
        ),
    ).add_to(m)

    folium.LayerControl().add_to(m)

    bounds = heat_map_gdf.total_bounds
    m.fit_bounds([
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]],
    ])

    return m

def run_analysis(api_key, date, time_str, granularity):
    # San Jose AOI from the notebook.
    san_jose_aoi = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "San Jose Study Area"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-121.950, 37.300],
                    [-121.850, 37.300],
                    [-121.850, 37.380],
                    [-121.950, 37.380],
                    [-121.950, 37.300],
                ]],
            },
        }],
    }

    activity_id = submit_heatmap(
        api_key, san_jose_aoi, date, time_str, granularity
    )
    result = wait_for_activity(api_key, activity_id)

    # Handle the API response wrappers used in the notebook.
    heatmap_result = result
    if "data" in heatmap_result:
        heatmap_result = heatmap_result["data"]
    if "result" in heatmap_result:
        heatmap_result = heatmap_result["result"]

    map_data = heatmap_result.get("map_data", {})
    stats_data = heatmap_result.get("stats_data", {})

    heat_gdf = build_risk_engine(map_data)
    return heat_gdf, stats_data, activity_id

st.markdown("""
<div class="hero">
<h1>🔥 HeatShield AI</h1>
<p>AI-powered urban heat-risk mapping for resilient cities & infrastructure</p>
</div>
""", unsafe_allow_html=True)

api_key = get_api_key()

if not api_key:
    st.error(
        "FortyGuard API key is not configured. "
        "Add FORTYGUARD_API_KEY in Streamlit Community Cloud → App settings → Secrets."
    )
    st.stop()

with st.sidebar:
    st.header("Analysis Controls")
    analysis_date = st.date_input(
        "Date",
        value=pd.Timestamp("2026-08-29").date(),
    )
    analysis_time = st.time_input(
        "Time",
        value=pd.Timestamp("14:00").time(),
    )
    granularity = st.selectbox(
        "Spatial granularity",
        [100, 250, 500],
        index=0,
        help="100 matches the working notebook configuration.",
    )
    run = st.button("🔥 Run Heat Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    st.caption("Track 1 · Resilient Cities & Infrastructure")
    st.caption("Data source: FortyGuard Temperature API")
    st.caption("Map tiles: OpenStreetMap")

if run or "heat_gdf" not in st.session_state:
    if run:
        with st.spinner(
            "FortyGuard is generating the heatmap and HeatShield is scoring the zones..."
        ):
            try:
                heat_gdf, stats_data, activity_id = run_analysis(
                    api_key,
                    str(analysis_date),
                    str(analysis_time.strftime("%H:%M")),
                    granularity,
                )
                st.session_state.heat_gdf = heat_gdf
                st.session_state.stats_data = stats_data
                st.session_state.activity_id = activity_id
                st.success("Heat analysis completed.")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()
    else:
        # First load: automatically run the notebook's known-working defaults.
        with st.spinner("Loading the default San Jose heat-risk analysis..."):
            try:
                heat_gdf, stats_data, activity_id = run_analysis(
                    api_key, "2026-08-29", "14:00", 100
                )
                st.session_state.heat_gdf = heat_gdf
                st.session_state.stats_data = stats_data
                st.session_state.activity_id = activity_id
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

heat_gdf = st.session_state.heat_gdf
stats_data = st.session_state.get("stats_data", {})
activity_id = st.session_state.get("activity_id", "—")

critical = int((heat_gdf["risk_level"] == "CRITICAL").sum())
high = int((heat_gdf["risk_level"] == "HIGH").sum())
moderate = int((heat_gdf["risk_level"] == "MODERATE").sum())
low = int((heat_gdf["risk_level"] == "LOW").sum())

avg_temp = heat_gdf["average_temperature"].mean()
max_temp = heat_gdf["max_temperature"].max()
avg_risk = heat_gdf["risk_score"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
for col, label, value in [
    (c1, "Average Temperature", f"{avg_temp:.1f} °C"),
    (c2, "Maximum Temperature", f"{max_temp:.1f} °C"),
    (c3, "Average Risk", f"{avg_risk:.1f}/100"),
    (c4, "High-Risk Zones", f"{high:,}"),
    (c5, "Critical Zones", f"{critical:,}"),
]:
    with col:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("### 🗺️ Interactive Heat-Risk Map")
st.caption(
    "Hover over a tile to inspect temperature, risk score, classification, and recommended intervention."
)
st_folium(make_map(heat_gdf), use_container_width=True, height=650)

left, right = st.columns([1.15, 1])

with left:
    st.markdown("### 🚨 Hotspot Priorities")
    hotspots = (
        heat_gdf[
            heat_gdf["risk_level"].isin(["CRITICAL", "HIGH"])
        ]
        .sort_values("risk_score", ascending=False)
        [["tile_id", "average_temperature", "risk_score",
          "risk_level", "recommendation"]]
        .head(15)
        .copy()
    )
    st.dataframe(
        hotspots,
        use_container_width=True,
        hide_index=True,
        column_config={
            "average_temperature": st.column_config.NumberColumn(
                "Temperature °C", format="%.2f"
            ),
            "risk_score": st.column_config.NumberColumn(
                "Risk Score", format="%.1f"
            ),
        },
    )

with right:
    st.markdown("### 📊 Risk Distribution")
    distribution = pd.DataFrame({
        "Risk Level": ["CRITICAL", "HIGH", "MODERATE", "LOW"],
        "Zones": [critical, high, moderate, low],
    })
    st.bar_chart(distribution.set_index("Risk Level"))

    st.markdown("### 🏙️ Intervention Logic")
    st.write("**CRITICAL:** Priority cooling + shade + trees + cool surfaces")
    st.write("**HIGH:** Shade infrastructure + tree canopy")
    st.write("**MODERATE:** Increase vegetation + reflective surfaces")
    st.write("**LOW:** Maintain existing cooling infrastructure")

with st.expander("Temperature statistics from FortyGuard"):
    temperature_stats = stats_data.get("temperature_stats", {})
    st.json(temperature_stats)

with st.expander("Methodology"):
    st.markdown("""
**HeatShield risk score**

- Temperature score: normalized 0–100 within the returned heatmap.
- Persistence score: **50** baseline because this implementation is a spatial snapshot and does not claim historical persistence.
- Exceedance score: temperature above **32°C**, scaled over an 8°C range and clipped to 0–100.
- Final risk = **60% temperature + 25% persistence + 15% exceedance**.
- Classification: **80+ Critical, 60+ High, 40+ Moderate, below 40 Low**.

These are the scoring rules implemented in the submitted HEATSHIELD notebook.
""")

st.markdown(
    f'<p class="small-note">FortyGuard activity: {activity_id} · '
    f'{len(heat_gdf):,} spatial tiles analyzed</p>',
    unsafe_allow_html=True,
)
