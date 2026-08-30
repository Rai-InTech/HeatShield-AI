# 🔥 HeatShield AI

### AI-Powered Urban Heat-Risk Mapping for Resilient Cities & Infrastructure

> **From temperature data to city-scale action.**
>
> HeatShield AI turns fine-grained temperature observations into an interactive urban heat-risk map, hotspot classifications, and practical infrastructure recommendations for more heat-resilient cities.

<p align="center">
  <a href="https://heatshield-ai.streamlit.app/">🚀 Live Demo</a> •
  <a href="https://github.com/Rai-InTech/HeatShield-AI">💻 GitHub Repository</a>
</p>

---

## 🌡️ Why HeatShield?

Extreme urban heat is not experienced uniformly across a city. Small geographic areas can experience meaningfully different temperatures, creating localized heat hotspots that require targeted interventions.

HeatShield AI is designed around a simple question:

> **Where is heat risk concentrated, and what should a city do about it?**

The system uses the **FortyGuard Temperature API** to obtain spatial temperature data, processes the resulting geographic tiles, calculates heat-risk scores, identifies priority hotspots, and translates those results into actionable urban interventions.

---

## ✨ What It Does

- 🛰️ Retrieves spatial temperature data through the **FortyGuard Temperature API**
- 🗺️ Processes temperature observations as geographic tiles
- 📊 Calculates temperature statistics and normalized heat scores
- 🔥 Produces a composite heat-risk score for each spatial tile
- 🚨 Classifies locations into **LOW, MODERATE, HIGH,** and **CRITICAL** risk
- 🌳 Generates intervention recommendations for priority areas
- 🌍 Visualizes results through an interactive map
- 📋 Surfaces high-priority hotspots in a decision-friendly dashboard

---

## 🧠 Heat-Risk Engine

HeatShield combines three signals into a single 0–100 risk score:

| Component | Weight | Purpose |
|---|---:|---|
| 🌡️ Temperature Score | **60%** | Captures the relative temperature intensity across the study area |
| 🔁 Persistence Score | **25%** | Represents the persistence component used by the current analysis |
| ☀️ Exceedance Score | **15%** | Measures how strongly temperature exceeds the defined threshold |

### Risk classification

| Risk Score | Classification |
|---:|---|
| **80–100** | 🔴 CRITICAL |
| **60–79.99** | 🟠 HIGH |
| **40–59.99** | 🟡 MODERATE |
| **0–39.99** | 🟢 LOW |

The implementation in `HEATSHIELD.ipynb` contains the original analysis workflow and scoring logic used by the project.

---

## 🌳 From Risk to Action

HeatShield is designed to move beyond simply displaying a heatmap.

| Risk level | Example intervention direction |
|---|---|
| 🔴 **CRITICAL** | Priority cooling, shade, tree canopy, and cool-surface interventions |
| 🟠 **HIGH** | Shade infrastructure and increased tree canopy |
| 🟡 **MODERATE** | Vegetation improvements and reflective/cool surfaces |
| 🟢 **LOW** | Maintain existing cooling infrastructure |

This creates a simple decision-support loop:

**Temperature → Risk → Hotspot → Intervention**

---

## 🗺️ Interactive Dashboard

The public Streamlit application provides:

- Average and maximum temperature
- Average heat-risk score
- Number of high-risk zones
- Number of critical zones
- Interactive geographic heat-risk map
- Tile-level temperature and risk inspection
- Hotspot prioritization
- Recommended interventions

### 🚀 Try it live

**https://heatshield-ai.streamlit.app/**

---

## 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │ FortyGuard Temperature  │
                    │          API            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Spatial Temperature     │
                    │ Data / GeoJSON Tiles    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Geospatial Processing   │
                    │ GeoPandas / Shapely     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Heat-Risk Engine        │
                    │ Temperature +          │
                    │ Persistence +           │
                    │ Exceedance              │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Hotspot Classification  │
                    │ + Intervention Logic    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Streamlit Dashboard     │
                    │ Interactive Heat Map    │
                    └─────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python**
- **FortyGuard Temperature API**
- **Pandas / NumPy** — numerical analysis
- **GeoPandas / Shapely** — geospatial processing
- **Folium** — interactive mapping
- **Streamlit** — public web dashboard
- **GitHub** — source control and project documentation
- **Streamlit Community Cloud** — deployment

---

## 📁 Repository Structure

```text
HeatShield-AI/
│
├── app.py                 # Streamlit web application
├── HEATSHIELD.ipynb       # Original executable analysis notebook
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Prevents secrets/local files from being committed
```

The notebook is intentionally included alongside the Streamlit application so the underlying analysis workflow can be inspected independently of the public UI.

---

## 🔐 API Key Security

The FortyGuard API key is **not committed to this repository**.

For the deployed Streamlit application, the key is provided through **Streamlit Secrets** as:

```toml
FORTYGUARD_API_KEY = "your-key-here"
```

For local development, keep the key in your local secret/environment configuration and never commit it to GitHub.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Rai-InTech/HeatShield-AI.git
cd HeatShield-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a local Streamlit secrets file:

```text
.streamlit/secrets.toml
```

Add:

```toml
FORTYGUARD_API_KEY = "your-key-here"
```

### 4. Launch the dashboard

```bash
streamlit run app.py
```

---

## 📓 Notebook

`HEATSHIELD.ipynb` contains the underlying project workflow, including:

1. FortyGuard API authentication
2. Heatmap submission
3. Activity polling until completion
4. GeoJSON map-data extraction
5. Temperature statistics
6. Geospatial tile construction
7. Heat-risk scoring
8. Risk classification
9. Intervention recommendations
10. Interactive visualization

The notebook's executed workflow demonstrates a completed FortyGuard heatmap request and processing of thousands of spatial tiles.

---

## 🎯 Hackathon Track

**FortyGuard Temperature API Hackathon — Track 1: Resilient Cities & Infrastructure**

HeatShield AI focuses on turning high-resolution temperature intelligence into a practical urban resilience tool for planners, infrastructure teams, and city decision-makers.

---

## 👤 Built Solo

**HeatShield AI** was developed as a solo AIML project for the FortyGuard Temperature API hackathon.

The goal was not simply to visualize temperature, but to create a compact decision-support workflow that connects:

> **Data → Spatial Intelligence → Risk → Action**

---

## 🔗 Links

- 🚀 **Live Demo:** https://heatshield-ai.streamlit.app/
- 💻 **GitHub:** https://github.com/Rai-InTech/HeatShield-AI

---

## 🔥 HeatShield AI

**See the heat. Score the risk. Prioritize the response.**
