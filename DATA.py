import pandas as pd
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np
from dash import dash_table
data_death = pd.read_csv("https://drive.google.com/uc?id=1XCaNbPYVu7TNZjLPsgQUnuTOspRIKRwH")
data_confirmed = pd.read_csv('https://drive.google.com/uc?id=1mYwudl_KKAwFoS7GhY-I1Xl4hQI3npPc')
data_death_filtered = data_death[['Country/Region' , '3/9/23','Province/State']]
data_confirmed_filtered = data_confirmed[['Country/Region' , '3/9/23','Province/State']]
data_death_filtered = data_death_filtered[data_death_filtered['Province/State'].isnull()]
data_confirmed_filtered = data_confirmed_filtered[data_confirmed_filtered['Province/State'].isnull()]
data_death_filtered = data_death_filtered.rename(columns={"3/9/23": "Deaths",'Country/Region' : 'Country'})
data_confirmed_filtered = data_confirmed_filtered.reindex(columns={"3/9/23": "Confirmed",'Country/Region' : 'Country'})
data_confirmed_filtered = data_confirmed_filtered.rename(columns={"3/9/23": "Confirmed",'Country/Region' : 'Country'})
df = pd.merge(data_confirmed_filtered, data_death_filtered, on="Country", how="outer")
df['Country'] = df['Country'].replace('US', 'United States')
df = df[['Country','Confirmed','Deaths']]

population = pd.read_csv(r'C:\Users\Utilisateur\Downloads\world_population.csv')
population = population.rename(columns={"Country/Territory": "Country"})
population['Country'] = population['Country'].str.upper()
df['Country'] = df['Country'].str.upper()
df_filtrer = pd.merge(df, population, on="Country")
df_filtrer = df_filtrer.rename(columns={"2022 Population": "Population"})
df_filtrer = df_filtrer[['Country','Confirmed','Deaths','Population']]
df_filtrer['Proportion (%)'] = df_filtrer['Deaths'] * 100  / df_filtrer['Population']
european_countries = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", 
    "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", 
    "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", 
    "France", "Georgia", "Germany", "Greece", "Hungary", 
    "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", 
    "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", 
    "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", 
    "Norway", "Poland", "Portugal", "Romania", "Russia", 
    "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", 
    "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", 
    "Vatican City"
]
df_europe_death = data_death[data_death['Country/Region'].isin(european_countries)]
#selectionner les date columns 
date_columns = df_europe_death.columns[4:]
deaths_by_date = df_europe_death[date_columns].sum()
deaths_by_date
# Transformer la Series en DataFrame
deaths_df = deaths_by_date.reset_index()
# Renommer les colonnes
deaths_df.columns = ["Date", "Deaths"]
df_europe_confirmed = data_confirmed[data_confirmed['Country/Region'].isin(european_countries)]
#selectionner les date columns 
date_columns = df_europe_confirmed.columns[4:]
confirmed_by_date = df_europe_confirmed[date_columns].sum()
# Transformer la Series en DataFrame
confirmed_df = confirmed_by_date.reset_index()
# Renommer les colonnes
confirmed_df.columns = ["Date", "Confirmed"]
df_date = pd.merge(confirmed_df, deaths_df, on="Date")
pays_capitalises = [pays.upper() for pays in european_countries]
# filtrer les pays européens 
df_table = df[df['Country'].isin(pays_capitalises)]
df_table['Deaths/Confirmed (%)'] = df_table['Deaths'] * 100 / df_table['Confirmed']
df_table = df_table.sort_values(by='Deaths/Confirmed (%)' ,ascending= False)  # trier  par rapport Deaths/Confirmed
df_table = df_table.reset_index(drop = True) # refaire l'index des pays pour qu'il soit ordonné
top_10 = df_table.tail(10)
top_10 = top_10.sort_values(by = 'Deaths/Confirmed (%)' )
last_10 = df_table.head(10)



#dash application

import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Charger les données COVID-19 (remplace par ton propre jeu de données)
# Exemple de DataFrame, tu devras l'ajuster en fonction de tes données

# Initialiser l'application Dash
app = dash.Dash(__name__)

custom_colorscale = ["#08da55", "#f9d107", "#fe0e0e"]  # Bleu, Jaune, Rouge

# Définir la disposition de l'application avec Dropdown et Graph , table , 
app.layout = html.Div(
    children=[
        html.H1("COVID-19: Cas confirmés et nombre de décès par pays", style={"textAlign": "center"}),
        dcc.Dropdown(
            id="dropdown-key",
            options=[
                {"label": "Cas confirmés", "value": "Confirmed"},
                {"label": "Décès", "value": "Deaths"},
                {"label": "Proportion des Décès par rapport à la population", "value": "Proportion (%)"},
                {"label": "Population", "value": "Population"}
            ],
            value="Confirmed",  # Valeur par défaut
            style={"width": "70%", "margin": "0 auto", "marginBottom": "20px"}
        ),
        dcc.Graph(id="choropleth-map"),  # Carte choroplèthe
        html.H1("Graphe des cas confirmés et décès en Europe par rapport au temp", style={"textAlign": "center"}),
        dcc.Dropdown(
            id='drop_graphe',
            options=[
                {'label': 'Cas confirmés', 'value': 'Confirmed'},
                {'label': 'Décès', 'value': 'Deaths'}
            ],
            value="Confirmed",  # Valeur par défaut
            style={"width": "70%", "margin": "0 auto", "marginBottom": "20px"}
        ),
        dcc.Graph(id='xy-graph'),  # Graphique des cas confirmés et décès
        html.H1("Classement des pays européens du nombre de décès sur total des cas confirmés: 10 premiers, 10 derniers", style={"textAlign": "center"}),

        # Dropdown pour basculer entre Top 10 et Last 10
        dcc.Dropdown(
            id="dropdown-table",
            options=[
                {"label": "Top 10", "value": "top"},
                {"label": "Last 10", "value": "last"}
            ],
            value="top",  # Valeur par défaut
            style={"width": "50%", "margin": "0 auto", "marginBottom": "20px"}
        ),

        # Tableau interactif
        dash_table.DataTable(
            id="data-table",
            columns=[
                {"name": col, "id": col} for col in df_table.columns
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "10px"},
            style_header={"backgroundColor": "lightblue", "fontWeight": "bold"},
        )
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "flex-start",
        "height": "100vh"
    }
)

# Callback pour mettre à jour la carte choroplèthe
@app.callback(
    Output("choropleth-map", "figure"),
    Input("dropdown-key", "value")
)

def update_map(selected_key):
    fig = px.choropleth(
        df_filtrer,
        locations="Country",
        locationmode="country names",
        color=selected_key,
        hover_name="Country",
        hover_data={selected_key: True},
        title=f"Carte basée sur {selected_key}",
        color_continuous_scale=custom_colorscale
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=600,
        width=1000
    )
    return fig

# Callback pour mettre à jour le graphique en fonction du dropdown
@app.callback(
    Output('xy-graph', 'figure'),
    Input('drop_graphe', 'value')
)
def update_graph(selected_key):
    fig = px.bar(
        df_date,
        x="Date",
        y=selected_key,
        title=f"{selected_key} par pays",
        labels={selected_key: selected_key, "Country": "Pays"},
        color=selected_key
        
    )
    fig.update_layout(
        height=600,
        width=1000,
        title=f"Graphe of {selected_key} In Europe based in time"
    )
    return fig
@app.callback(
    Output("data-table", "data"),
    Input("dropdown-table", "value")
)
def update_table(selected_option):
    if selected_option == "top":
        return top_10.to_dict("records")
    elif selected_option == "last":
        return last_10.to_dict("records")

# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True, port=8083)
    
