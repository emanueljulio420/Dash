import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("netflix_users.csv")
df['Last_Login'] = pd.to_datetime(df['Last_Login'])
df['Login_Month'] = df['Last_Login'].dt.to_period('M').astype(str)

default_theme = dbc.themes.FLATLY

app = dash.Dash(__name__, external_stylesheets=[default_theme])
app.title = "USUARIOS EN NETFLIX"
app.config.suppress_callback_exceptions = True
server = app.server

CONTENT_STYLE = {
    "padding": "2rem 1rem",
}

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="main-content", style=CONTENT_STYLE)
])

@app.callback(
    Output("main-content", "children"),
    Input("url", "pathname")
)
def render_main(pathname):
    return dbc.Container([
        html.H1("USUARIOS EN NETFLIX", className="text-center my-4"),

        dbc.Row([
            dbc.Col([
                html.H5("Usuarios por País"),
                dcc.Dropdown(
                    options=[{'label': c, 'value': c} for c in df['Country'].unique()],
                    value=df['Country'].unique()[0],
                    id='dropdown-country'
                ),
                dcc.Graph(id='bar-country')
            ], width=6),

            dbc.Col([
                html.H5("Tiempo de visualización por mes"),
                dcc.Graph(id='line-watchtime'),
                dcc.RangeSlider(
                    id='month-slider',
                    min=0,
                    max=len(df['Login_Month'].unique()) - 1,
                    value=[0, 5],
                    marks={i: month for i, month in enumerate(sorted(df['Login_Month'].unique()))},
                    step=1
                )
            ], width=6),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Distribución por Tipo de Suscripción"),
                dcc.RadioItems(
                    options=[
                        {"label": "Pastel", "value": "pie"},
                        {"label": "Barra", "value": "bar"}
                    ],
                    value="pie",
                    id="graph-type-selector"
                ),
                dcc.Graph(id="subscription-graph")
            ], width=6),

            dbc.Col([
                html.H5("Géneros más vistos por tipo de suscripción"),
                dcc.Dropdown(
                    options=[{'label': sub, 'value': sub} for sub in df['Subscription_Type'].unique()],
                    value=df['Subscription_Type'].unique()[0],
                    id='subscription-filter'
                ),
                dcc.Graph(id='genre-bar-graph')
            ], width=6),
        ])
    ], fluid=True)

@app.callback(
    Output('bar-country', 'figure'),
    Input('dropdown-country', 'value')
)
def update_country_graph(selected_country):
    filtered = df[df['Country'] == selected_country]
    fig = px.bar(filtered, x='Favorite_Genre', y='Watch_Time_Hours', color='Subscription_Type')
    fig.update_layout(title=f"Horas vistas por género en {selected_country}")
    return fig

@app.callback(
    Output('line-watchtime', 'figure'),
    Input('month-slider', 'value')
)
def update_line_chart(month_range):
    months = sorted(df['Login_Month'].unique())
    selected_months = months[month_range[0]:month_range[1] + 1]
    filtered = df[df['Login_Month'].isin(selected_months)]
    grouped = filtered.groupby('Login_Month')['Watch_Time_Hours'].sum().reset_index()
    fig = px.line(grouped, x='Login_Month', y='Watch_Time_Hours', markers=True)
    fig.update_layout(title="Horas vistas por mes", xaxis_title="Mes", yaxis_title="Horas")
    return fig

@app.callback(
    Output("subscription-graph", "figure"),
    Input("graph-type-selector", "value")
)
def update_subscription_graph(graph_type):
    grouped = df['Subscription_Type'].value_counts().reset_index()
    grouped.columns = ['Subscription_Type', 'Count']
    if graph_type == "pie":
        fig = px.pie(grouped, values='Count', names='Subscription_Type', title='Tipos de Suscripción')
    else:
        fig = px.bar(grouped, x='Subscription_Type', y='Count', title='Tipos de Suscripción')
    return fig

@app.callback(
    Output('genre-bar-graph', 'figure'),
    Input('subscription-filter', 'value')
)
def update_genre_bar_chart(subscription_type):
    filtered = df[df['Subscription_Type'] == subscription_type]
    genre_grouped = filtered.groupby('Favorite_Genre')['Watch_Time_Hours'].sum().reset_index().sort_values(by='Watch_Time_Hours', ascending=False)

    fig = px.bar(
        genre_grouped,
        x='Favorite_Genre',
        y='Watch_Time_Hours',
        title=f"Géneros más vistos ({subscription_type})",
        labels={'Watch_Time_Hours': 'Horas de Visualización', 'Favorite_Genre': 'Género'},
        color='Favorite_Genre'
    )

    fig.update_layout(
        xaxis_title="Género",
        yaxis_title="Horas vistas",
        showlegend=False,
        template="plotly_white"
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True)
