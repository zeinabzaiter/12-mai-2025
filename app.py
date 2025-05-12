import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Charger les données
df = pd.read_excel("other Antibiotiques staph aureus.xlsx")
df = df[df["Week"].apply(lambda x: str(x).isdigit())].copy()
df["Week"] = df["Week"].astype(int)

# Colonnes % à afficher
columns_to_plot = [col for col in df.columns if col.startswith('%')]

st.title("📊 Dashboard - Résistance aux antibiotiques (Staph Aureus)")

# Barre de recherche
search = st.text_input("🔍 Rechercher un antibiotique", "")

# Filtrer les colonnes selon la recherche
filtered_cols = [col for col in columns_to_plot if search.lower() in col.lower()]
selected_ab = filtered_cols[0] if filtered_cols else columns_to_plot[0]

# Sélecteur de plage de semaines
min_week, max_week = int(df["Week"].min()), int(df["Week"].max())
week_range = st.slider("🗓️ Plage de semaines", min_week, max_week, (min_week, max_week))

# Filtrer les données
filtered_df = df[(df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1])]
data = filtered_df[["Week", selected_ab]].copy()
data[selected_ab] = pd.to_numeric(data[selected_ab], errors='coerce')

# Calcul des seuils Tukey
q1 = np.percentile(data[selected_ab].dropna(), 25)
q3 = np.percentile(data[selected_ab].dropna(), 75)
iqr = q3 - q1
lower = max(q1 - 1.5 * iqr, 0)
upper = q3 + 1.5 * iqr

# Tracer le graphique
fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Week"], y=data[selected_ab], mode='lines+markers', name=selected_ab))
fig.add_trace(go.Scatter(x=data["Week"], y=[lower]*len(data), mode='lines', name='Tukey bas', line=dict(dash='dash', color='red')))
fig.add_trace(go.Scatter(x=data["Week"], y=[upper]*len(data), mode='lines', name='Tukey haut', line=dict(dash='dash', color='red')))
fig.update_layout(title=f"Évolution de la résistance - {selected_ab}",
                  xaxis_title="Semaine",
                  yaxis_title="Résistance (%)",
                  yaxis=dict(range=[0, 20]),
                  hovermode="closest")

st.plotly_chart(fig, use_container_width=True)
