import dash_bootstrap_components as dbc
from dash import dcc, html

from accidentdashboard import utils
from accidentdashboard.data_lookup import accident_data_lookup
from accidentdashboard.layout import app_tabs


# HTML Layout using Bootstrap

def get_bootstrap_rows(accident_df):
    zoom_center = utils.zoom_center(accident_df['longitude'], accident_df['latitude'])

    no_loc_data = accident_df.drop(
        ['accident_index', 'accident_reference', 'location_easting_osgr', 'location_northing_osgr', 'longitude',
         'latitude', 'latitude', 'local_authority_ons_district', 'lsoa_of_accident_location'], axis=1)
    no_loc_data = no_loc_data.rename(columns={'date': 'month_of_year', 'time': 'hour_of_day'})
    # no_loc_data.columns.tolist()

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
                        dcc.Graph(id='crash_map',
                                  figure=utils.getmapfigure(accident_df, zoom_center[1]['lat'], zoom_center[1]['lon'],
                                                            zoom_center[0]), config={'editable': False,
                                                                                     'displayModeBar': True,
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
                    app_tabs.get_html_tabs(no_loc_data),
                ]), width=5),
            ]),
            dbc.Row([
                dbc.Col(html.Div(
                    "All data download from https://data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data"),
                    width=10),
            ]),
        ]
    )
    return bootstrap_rows
