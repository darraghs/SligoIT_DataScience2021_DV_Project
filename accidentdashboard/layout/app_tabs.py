import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
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
