import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

# Charger les données
df = pd.read_excel("other Antibiotiques staph aureus.xlsx")
df = df[df["Week"].apply(lambda x: str(x).isdigit())].copy()
df["Week"] = df["Week"].astype(int)

# Colonnes des % de résistance à analyser
columns_to_plot = [col for col in df.columns if col.startswith('%')]

# Fonction pour générer le graphique
def generate_figure(antibiotic, week_range):
    data = df[(df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1])]
    data = data[["Week", antibiotic]].copy()
    data[antibiotic] = pd.to_numeric(data[antibiotic], errors='coerce')
    q1 = np.percentile(data[antibiotic].dropna(), 25)
    q3 = np.percentile(data[antibiotic].dropna(), 75)
    iqr = q3 - q1
    lower_bound = max(q1 - 1.5 * iqr, 0)
    upper_bound = q3 + 1.5 * iqr

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["Week"],
        y=data[antibiotic],
        mode='lines+markers',
        name=antibiotic,
        hoverinfo='x+y'
    ))
    fig.add_trace(go.Scatter(
        x=data["Week"],
        y=[lower_bound] * len(data),
        mode='lines',
        name='Tukey Lower Bound',
        line=dict(dash='dash', color='red')
    ))
    fig.add_trace(go.Scatter(
        x=data["Week"],
        y=[upper_bound] * len(data),
        mode='lines',
        name='Tukey Upper Bound',
        line=dict(dash='dash', color='red')
    ))

    fig.update_layout(
        title=f"Évolution de la résistance - {antibiotic}",
        xaxis_title="Semaine",
        yaxis_title="Résistance (%)",
        yaxis=dict(range=[0, 20]),
        hovermode="closest"
    )
    return fig

# Création de l'application Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard - Résistance aux antibiotiques (Staph Aureus)"),
    html.Div([
        html.Label("Recherche d'antibiotique :"),
        dcc.Input(id='search-antibiotic', type='text', debounce=True, placeholder="ex: Daptomycin"),
    ], style={'margin-bottom': '10px'}),
    html.Div([
        html.Label("Plage de semaines :"),
        dcc.RangeSlider(
            id='week-range',
            min=df["Week"].min(),
            max=df["Week"].max(),
            value=[df["Week"].min(), df["Week"].max()],
            marks={i: str(i) for i in range(df["Week"].min(), df["Week"].max()+1, 5)},
            step=1
        )
    ], style={'margin-bottom': '30px'}),
    dcc.Graph(id='resistance-graph')
])

@app.callback(
    Output('resistance-graph', 'figure'),
    Input('search-antibiotic', 'value'),
    Input('week-range', 'value')
)
def update_graph(search_value, week_range):
    if search_value:
        matching = [col for col in columns_to_plot if search_value.lower() in col.lower()]
        if matching:
            return generate_figure(matching[0], week_range)
    return generate_figure(columns_to_plot[0], week_range)

if __name__ == "__main__":
    app.run_server(debug=True)
