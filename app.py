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

# Tabs for visual content
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Label("X-Axis"),
            dcc.Dropdown(id="graph_x_select",
                         options=[{'label': str(b[1]), 'value': b[0]} for b in
                                  accident_data_lookup.accident_data_lookup[
                                      'local_authority_district'].items()],
                         multi=False,
                         value=[],
                         ),
            dbc.Label("Y-Axis"),
            dcc.Dropdown(id="graph_y_select",
                         options=[{'label': str(b[1]), 'value': b[0]} for b in
                                  accident_data_lookup.accident_data_lookup[
                                      'local_authority_district'].items()],
                         multi=False,
                         value=[],
                         ),
            #dcc.Graph(id='graph_viz', figure=None, config={'editable': False,
            #                                                                          'displaylogo': False,
            #                                                                          'modeBarButtonsToRemove': [
            #                                                                              'lasso2d',
            #                                                                              'toImage',
            #                                                                              'autoScale2d',
            #                                                                              'resetScale2d',
            #                                                                              'select2d'
            #                                                                          ]
            #                                                                          }, )

        ], style={'min-height': '750px'}
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(dash_table.DataTable(
                id='statistics_table',
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
                style_header=dict(backgroundColor="lightgrey"),
                style_data=dict(backgroundColor="white"),
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'right'
                    } for c in ['values']
                ],
                style_as_list_view=True,
                page_size=20
            )),

        ], style={'min-height': '750px'}
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(dash_table.DataTable(
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
                style_header=dict(backgroundColor="lightgrey"),
                style_data=dict(backgroundColor="white"),
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'right'
                    } for c in ['values']
                ],
                style_as_list_view=True,
                page_size=20
            ))

        ], style={'min-height': '750px'}
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Graph"),
        dbc.Tab(tab2_content, label="Statistics"),
        dbc.Tab(tab3_content, label="Details"),
    ]
)

# HTML Layout using Bootstrap
bootstrap_rows = html.Div(
    [
        dbc.Row(html.Hr()),
        dbc.Row(dbc.Col(html.H2("UK Accident Dashboard", style={'text-align': 'center'}))),
        dbc.Row(html.Hr()),
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H5("Filter By"),
                    dbc.Row(
                        dbc.Col(
                            html.Div([
                                html.Hr(),
                                dbc.Label("Year"),
                                dcc.Dropdown(id="select_year",
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
                    ),

                    dbc.Row(
                        dbc.Col(
                            html.Div([
                                html.Hr(),
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
                                html.Hr(),
                                dbc.Label("Local Authority"),

                                dcc.Dropdown(id="select_local_authority",
                                             options=[{'label': str(b[1]), 'value': b[0]} for b in
                                                      accident_data_lookup.accident_data_lookup[
                                                          'local_authority_district'].items()],
                                             multi=True,
                                             value=[],
                                             ),

                            ])
                        )
                    )

                ])
                , width=2
            ),

            dbc.Col(
                html.Div(
                    dcc.Graph(id='crash_map', figure=utils.getmapfigure(accident_df), config={'editable': False,
                                                                                              'displaylogo': False,
                                                                                              'modeBarButtonsToRemove': [
                                                                                                  'lasso2d',
                                                                                                  'toImage',
                                                                                                  'autoScale2d',
                                                                                                  'resetScale2d',
                                                                                                  'select2d'
                                                                                              ]
                                                                                              }, )
                ), width=5
            ),

            dbc.Col(html.Div([
                tabs,
            ]), width=5),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='Coordinates'), width=10),
        ]),
    ]
)

app.layout = dbc.Container(
    bootstrap_rows, fluid=True
)


# ------------------------------------------------------------------------------
# Connect the map component
@app.callback(
    [Output('crash_table', 'data'),
     Output(component_id='crash_map', component_property='figure')],
    [Input(component_id='select_year', component_property='value'),
     Input('severity-input', 'value'),
     Input('select_local_authority', 'value'),
     Input('crash_map', 'clickData'),
     ]
)
def update_map(year_selected, severity, local_auth_selected, marker_selection, ):
    if year_selected is not None and len(severity) > 0:
        global accident_df

        triggered_id = callback_context.triggered[0]['prop_id']
        if triggered_id in ['select_year.value', 'severity-input.value', 'select_local_authority.value']:
            fig = apply_map_fitlers(year_selected, severity, local_auth_selected, False)
            return [], fig
        else:
            return update_accident_table(marker_selection), dash.no_update
    return dash.no_update, dash.no_update


def apply_map_fitlers(year, severities, local_auth_selected, reset_zoom=False):
    accident_df = utils.getaccidentdf(year)
    print(f'Shape before filering: {accident_df.shape}')
    accident_df = accident_df[accident_df['accident_severity'].isin(severities)].copy()
    if len(local_auth_selected) > 0:
        accident_df = accident_df[accident_df['local_authority_district'].isin(local_auth_selected)].copy()
    print(f'Shape after filering: {accident_df.shape}')
    fig = utils.getmapfigure(accident_df, reset_zoom)
    return fig


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
                if len(accident_data[i].values) > 0:
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
                    print(f'No values for label: {i}')
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
