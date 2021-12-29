import numpy
from dash import Dash, dcc, html, Input, Output, dash_table  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc

from accidentdashboard import utils, accident_data_lookup

accident_df = utils.getaccidentdf(2020)

external_stylesheets=[dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname='/dav2021/')

server = app.server

badge = dbc.Button(
    [
        "Notifications",
        dbc.Badge("4", color="light", text_color="primary", className="ms-1"),
    ],
    color="primary",
)
app.layout = dbc.Container(badge, fluid=True)

row = html.Div(
    [
        dbc.Row(dbc.Col( html.H1("UK Accident Dashboard", style={'text-align': 'center'}) )),
        dbc.Row(dbc.Col(html.Div(dcc.Dropdown(id="slct_year",
                                              options=[
                                                  {"label": "2016", "value": 2016},
                                                  {"label": "2017", "value": 2017},
                                                  {"label": "2018", "value": 2018},
                                                  {"label": "2019", "value": 2019},
                                                  {"label": "2020", "value": 2020}],
                                              multi=False,
                                              value=2020,
                                              style={'width': "40%"}
                                              )))),
        dbc.Row(
            [
                dbc.Col(html.Div("One of three columns")),
                dbc.Col(html.Div("One of three columns")),
                dbc.Col(html.Div("One of three columns")),
            ]
        ),
    ]
)



app.layout = html.Div([



    row,

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='crash_map', figure=utils.getmapfigure(accident_df)),
    html.Div(id='Coordinates'),
    html.Div(id='Points', children=[]),
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i}
                     for i in accident_data_lookup.accident_data_lookup.keys()],
            data=[],
            style_cell=dict(textAlign='left'),
            style_header=dict(backgroundColor="paleturquoise"),
            style_data=dict(backgroundColor="lavender")
        )
    ])

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='crash_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_map(option_slctd):
    global accident_df
    accident_df = utils.getaccidentdf(option_slctd)
    container = "The year chosen by user was: {}".format(option_slctd)
    fig = utils.getmapfigure(accident_df)

    return container, fig


@app.callback(
    Output('table', 'data'),
    [Input('crash_map', 'clickData')])
def update_accident_table(selection):
    if selection is not None:
        global accident_df
        accident_index = selection["points"][0]["customdata"][0]
        accident_data = accident_df[accident_df['accident_index'] == accident_index].copy()

        for i in accident_data:
            if i in accident_data_lookup.accident_data_lookup.keys():
                lookup = accident_data_lookup.accident_data_lookup[i]
                value = accident_data[i].values[0]
                if isinstance(value, numpy.int64):
                    value = value.item()

                if isinstance(value, int) and value >= 0 and value in lookup:
                    accident_data[i] = lookup[value]
                elif isinstance(value, str) and value in lookup:
                    accident_data[i] = lookup[value]
                elif isinstance(value, int) and value == -1:
                    accident_data[i] = 'Data missing or out of range'
                else:
                    print(f' Could not find value: {value}, type: {type(value)} in lookup: {lookup} for key: {i}')

        return accident_data.to_dict('records')


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
