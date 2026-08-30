# HeatShield AI

AI-powered urban heat-risk mapping for resilient cities and infrastructure.

## Demo
Deployed with Streamlit Community Cloud.

## Project structure
- `app.py` — Streamlit demo wrapper
- `HEATSHIELD.ipynb` — original notebook containing the full analysis
- `requirements.txt` — deployment dependencies
- `.gitignore` — prevents local secrets from being committed

## Secret
Configure `FORTYGUARD_API_KEY` in Streamlit Community Cloud App Settings → Secrets. Do not commit `.streamlit/secrets.toml`.

## Method
The app reuses the notebook's FortyGuard heatmap request, response parsing, risk scoring, hotspot classification, recommendations, and Folium visualization.
