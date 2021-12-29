import dash
import dash_bootstrap_components as dbc
import numpy
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, \
    callback_context  # pip install dash (version 2.0.0 or higher)

from accidentdashboard import utils, accident_data_lookup

accident_df = utils.getaccidentdf(2020)

app = Dash("UK Accident Dashboard", external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname='/dav2021/')

server = app.server

# HTML Layout using Bootstrap
bootstrap_rows = html.Div(
    [
        dbc.Row(dbc.Col(html.H1("UK Accident Dashboard", style={'text-align': 'center'}))),
        dbc.Row([ dbc.Col(html.Div("Select year: ")), dbc.Col(html.Div(dcc.Dropdown(id="slct_year",
                                              options=[
                                                  {"label": "2016", "value": 2016},
                                                  {"label": "2017", "value": 2017},
                                                  {"label": "2018", "value": 2018},
                                                  {"label": "2019", "value": 2019},
                                                  {"label": "2020", "value": 2020}],
                                              multi=False,
                                              value=2020,
                                              style={'width': "40%"}
                                              )))]),
        dbc.Row([
            dbc.Col( html.Div("Map")),
            dbc.Col(html.Div("Graphs")),
            dbc.Col(html.Div("Individual Accident Info"))
        ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(dcc.Graph(id='crash_map', figure=utils.getmapfigure(accident_df)))),
                dbc.Col(html.Div("Graphs")),
                dbc.Col(html.Div([
                    dash_table.DataTable(
                        id='crash_table',
                        columns=[{"name": i, "id": i}
                                 for i in ['labels', 'values']],
                        data=[],
                        style_cell=dict(textAlign='left'),
                        style_header=dict(backgroundColor="paleturquoise"),
                        style_data=dict(backgroundColor="lavender")
                    )
                ])),
            ]
        ),
        dbc.Row([
            dbc.Col( html.Div(id='output_container', children=[])),
            dbc.Col(html.Div(id='Coordinates')),
            dbc.Col(html.Div(id='Points', children=[]))
            ]
        ),
    ]
)

app.layout = bootstrap_rows


# ------------------------------------------------------------------------------
# Connect the map component
@app.callback(
    [Output('crash_table', 'data'),
     Output(component_id='output_container', component_property='children'),
     Output(component_id='crash_map', component_property='figure')],
    [Input('crash_map', 'clickData'),
     Input(component_id='slct_year', component_property='value')]
)
def update_map(marker_selection, option_slctd):
    if option_slctd is not None:
        global accident_df

        triggered_id = callback_context.triggered[0]['prop_id']
        if 'slct_year.value' == triggered_id:
            container = "The year chosen by user was: {}".format(option_slctd)
            accident_df = utils.getaccidentdf(option_slctd)
            fig = utils.getmapfigure(accident_df)
            return [], container, fig
        else:
            return update_accident_table(marker_selection), dash.no_update, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update


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

        conv_array = accident_data.values.tolist()
        key_array = list(accident_data.keys())

        DF_SIMPLE = pd.DataFrame({
            'labels': key_array,
            'values': conv_array[0]
        })
        return DF_SIMPLE.to_dict('records')
    return []


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
