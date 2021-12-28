
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

    html.H1("UK Accident Dashboard", style={'text-align': 'center'}),

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

    dcc.Graph(id='crash_map', figure={}),
    html.Div(id='Coordinates'),
    html.Div(id='Points', children=[]),
    html.Div([
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} 
                 for i in accident_2020_df.columns],
        data=accident_2020_df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    )


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
    
    token = open(".mapbox_token").read()

    container = "The year chosen by user was: {}".format(option_slctd)
    
    
    token = open(".mapbox_token").read()

    crash_colours = ['yellow','orange', 'red' ]

    crash_categories = accident_2020_df.accident_severity.unique()


    crash_dict = dict(zip(crash_categories,crash_colours)) #set up band to color substitution dict
    accident_2020_df['color'] = accident_2020_df['accident_severity'].replace(to_replace=crash_colours)

    accident_2020_df['accident_severity'] = accident_2020_df['accident_severity'].astype(str)

    fig = px.scatter_mapbox(accident_2020_df, lat="latitude", lon="longitude", hover_name="accident_severity", 
                        hover_data=["speed_limit", "number_of_vehicles"],
                        custom_data=['accident_index'],
                        color="accident_severity", 
                        color_discrete_sequence=crash_colours,
                        zoom=4, height=800, width=600)
    

    fig.update_layout(mapbox_style="open-street-map", mapbox_accesstoken=token)
    fig.update_mapboxes(center_lat=55, center_lon=-3.5)
    fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
    fig.update_layout(height=600)
        
    return container, fig

@app.callback(
        Output('Points', 'children'),
        [Input('crash_map', 'clickData')])
def plot_basin(selection):
    if selection is not None:
        accident_index = selection["points"][0]["customdata"][0]
        accident_data = accident_2020_df[ accident_2020_df['accident_index']==accident_index]
        print(f'Accident Data: {accident_data}')
        
        return accident_data
    

@app.callback(
    Output('Coordinates', 'children'),
    Input('crash_map', 'relayoutData'))
def display_relayout_data(relayoutData):
    try:
        coords = relayoutData['mapbox._derived']['coordinates']
        lon_min = coords[0][0]
        lon_max = coords[1][0]
        lat_min = coords[2][1]
        lat_max = coords[1][1]
        
        print(f'Min Lat: {lat_min}, Max Lat: {lat_max}, Min Lon:{lon_min}, Max Lon: {lon_max}')
        return [lat_min, lat_max, lon_min, lon_max]
    except:
        return []
    
if __name__ == '__main__':
    app.run_server(debug=True)
