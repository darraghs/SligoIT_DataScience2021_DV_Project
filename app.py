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
        dbc.Row(),
        dbc.Row(dbc.Col(html.H2("UK Accident Dashboard", style={'text-align': 'center'}))),
        dbc.Row(),
        dbc.Row([
            dbc.Col(html.H3("Filter"), width=2),
            dbc.Col(html.H3("Map"), width=5),
            dbc.Col(html.H3("Graphs"), width=5)
        ]),
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Row(
                        dbc.Col(
                            html.Div([
                                dbc.Label("Severity"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Fatal", "value": 1},
                                        {"label": "Serious", "value": 2},
                                        {"label": "Slight", "value": 3},
                                    ],
                                    value=[1, 2, 3],
                                    id="severity-input",
                                )
                            ])
                        )
                    ),

                    dbc.Row(
                        dbc.Col(
                            html.Div([
                                dbc.Label("Year"),
                                dcc.Dropdown(id="slct_year",
                                             options=[
                                                 {"label": "2016", "value": 2016},
                                                 {"label": "2017", "value": 2017},
                                                 {"label": "2018", "value": 2018},
                                                 {"label": "2019", "value": 2019},
                                                 {"label": "2020", "value": 2020}],
                                             multi=False,
                                             value=2020
                                             )
                            ])
                        )
                    )
                ])
                , width=2
            ),

            dbc.Col(
                html.Div(
                    dcc.Graph(id='crash_map', figure=utils.getmapfigure(accident_df))
                ), width=5
            ),

            dbc.Col(html.Div([

            ]), width=5),
        ]),
        dbc.Row([
            dbc.Col(html.H3("Filter"), width=2),
            dbc.Col(html.H3("Map"), width=5),
            dbc.Col(html.H3("Individual Crash"), width=5)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='output_container', children=[]), width=2),
            dbc.Col(html.Div(id='Coordinates'), width=5),
            dbc.Col(html.Div(dash_table.DataTable(
                id='crash_table',
                columns=[{"name": i, "id": i}
                         for i in ['labels', 'values']],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left'
                },
                style_header=dict(backgroundColor="paleturquoise"),
                style_data=dict(backgroundColor="lavender")
            )), width=5)
        ]
        ),
    ]
)

app.layout = dbc.Container(
    bootstrap_rows, fluid=True
)


# ------------------------------------------------------------------------------
# Connect the map component
@app.callback(
    [Output('crash_table', 'data'),
     Output(component_id='output_container', component_property='children'),
     Output(component_id='crash_map', component_property='figure')],
    [   Input('severity-input', 'value'),
        Input('crash_map', 'clickData'),
     Input(component_id='slct_year', component_property='value')]
)
def update_map(severity, marker_selection, option_slctd):
    if option_slctd is not None && len(severity)>0:
        global accident_df

        triggered_id = callback_context.triggered[0]['prop_id']
        if 'slct_year.value' == triggered_id:
            accident_df = utils.getaccidentdf(option_slctd)
            accident_df[accident_df['accident_index'].isin(severity)]
            fig = utils.getmapfigure(accident_df)
            return [], dash.no_update, fig
        elif 'severity-input.value' == triggered_id:
            accident_df = accident_df[accident_df['accident_index'].isin(severity)].copy()
            fig = utils.getmapfigure(accident_df)
            return [], dash.no_update, fig
        else:
            return update_accident_table(marker_selection), dash.no_update, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update


def update_accident_table(selection):
    if selection is not None:
        global accident_df
        accident_index = selection["points"][0]["customdata"][0]
        accident_data = accident_df[accident_df['accident_index'] == accident_index].copy()

        labels = []
        values = []

        for i in accident_data:
            if i in accident_data_lookup.accident_data_lookup.keys():
                lookup = accident_data_lookup.accident_data_lookup[i]
                value = accident_data[i].values[0]
                if isinstance(value, numpy.int64):
                    value = value.item()

                if isinstance(value, int) and value >= 0 and value in lookup:
                    labels.append(i.replace('_', ' '))
                    values.append(lookup[value])
                elif isinstance(value, str) and value in lookup:
                    labels.append(i.replace('_', ' '))
                    values.append(lookup[value])
                elif isinstance(value, int) and value == -1:
                    labels.append(i.replace('_', ' '))
                    values.append('Data missing or out of range')
                else:
                    print(f' Could not find value: {value}, type: {type(value)} in lookup: {lookup} for key: {i}')
            else:
                labels.append(i.replace('_', ' '))
                values.append(accident_data[i])

        DF_SIMPLE = pd.DataFrame({
            'labels': labels,
            'values': values
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
