import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# --- Chargement des données ---
df = pd.read_excel("other Antibiotiques staph aureus.xlsx")
df = df[df["Week"].apply(lambda x: str(x).isdigit())].copy()
df["Week"] = df["Week"].astype(int)

# --- Colonnes des pourcentages de résistance ---
columns_to_plot = [col for col in df.columns if col.startswith('%')]

st.title("📊 Dashboard - Résistance aux antibiotiques (Staph Aureus)")

# --- Sélecteur multiple des antibiotiques ---
selected_antibiotics = st.multiselect(
    "🧪 Sélectionner les antibiotiques à afficher",
    options=columns_to_plot,
    default=columns_to_plot  # Affiche tout par défaut
)

# --- Slider de plage de semaines ---
min_week, max_week = int(df["Week"].min()), int(df["Week"].max())
week_range = st.slider("📆 Plage de semaines", min_week, max_week, (min_week, max_week))

# --- Filtrage des données ---
filtered_df = df[(df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1])]

# --- Création de la figure Plotly ---
fig = go.Figure()

for ab in selected_antibiotics:
    data = filtered_df[["Week", ab]].copy()
    data[ab] = pd.to_numeric(data[ab], errors='coerce')

    q1 = np.percentile(data[ab].dropna(), 25)
    q3 = np.percentile(data[ab].dropna(), 75)
    iqr = q3 - q1
    lower = max(q1 - 1.5 * iqr, 0)
    upper = q3 + 1.5 * iqr

    fig.add_trace(go.Scatter(x=data["Week"], y=data[ab],
                             mode='lines+markers',
                             name=ab))
    fig.add_trace(go.Scatter(x=data["Week"], y=[upper]*len(data),
                             mode='lines', name=f"{ab} seuil haut",
                             line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=data["Week"], y=[lower]*len(data),
                             mode='lines', name=f"{ab} seuil bas",
                             line=dict(dash='dot')))

fig.update_layout(
    title="Évolution des % de résistance (avec seuils Tukey)",
    xaxis_title="Semaine",
    yaxis_title="Résistance (%)",
    yaxis=dict(range=[0, 20]),
    hovermode="x unified"
)

# --- Affichage du graphique ---
st.plotly_chart(fig, use_container_width=True)

