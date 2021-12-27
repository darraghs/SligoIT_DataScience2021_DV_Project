
import os

import pandas as pd

import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)


def getHour(timestr):
    return timestr.split(':')[0]
def getDate(datestr):
    return datestr.split('/')[1]
def correctTimestamp(timestamp):
    if type(timestamp) == 'str':
        return timestamp.replace('T', '')
    else:
        return timestamp

def cleanDF(dataframe):
    if 'accident_index' in dataframe.columns:
        dataframe['accident_index'] = dataframe['accident_index'].apply(correctTimestamp)
    if 'time' in dataframe.columns:
        dataframe['time'] = dataframe['time'].apply(getHour)
    if 'date' in dataframe.columns:
        dataframe['date'] = dataframe['date'].apply(getDate)


accident_2020_df=pd.read_csv(
    "data/dft-road-casualty-statistics-accident-2020.csv"
)
cleanDF(accident_2020_df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname='/dav2021/' )

server = app.server

app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018},
                     {"label": "2019", "value": 2019},
                     {"label": "2020", "value": 2020}],
                 multi=False,
                 value=2020,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='crash_map', figure={})

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='crash_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    #dff = df.copy()
    #dff = dff[dff["Year"] == option_slctd]
    #dff = dff[dff["Affected by"] == "Varroa_mites"]

    # Plotly Express
    
    fig = px.scatter_mapbox(accident_2020_df, lat="latitude", lon="longitude", hover_name="accident_severity", 
                        hover_data=["number_of_casualties", "number_of_vehicles"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=300)
    
    
    fig.update_mapboxes(center_lat=55, center_lon=-1.3, zoom=4)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
    fig.update_layout(height=600)


    return container, fig




if __name__ == '__main__':
    app.run_server(debug=True)
