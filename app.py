import dash
import dash_bootstrap_components as dbc
import numpy
import pandas as pd
from dash import Dash, Input, Output, callback_context  # pip install dash (version 2.0.0 or higher)

from accidentdashboard import utils
from accidentdashboard.data_lookup import accident_data_lookup
from accidentdashboard.layout import bootstrap_rows

accident_df = utils.getaccidentdf(2020)
lat_min = accident_df['latitude'].min()
lat_max = accident_df['latitude'].max()
lon_min = accident_df['longitude'].min()
lon_max = accident_df['longitude'].max()

dash_app = Dash("UK Accident Dashboard", external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname='/dav2021/')

server = dash_app.server

dash_app.layout = dbc.Container(
    bootstrap_rows.get_bootstrap_rows(accident_df), fluid=True
)


# ------------------------------------------------------------------------------
# Connect the map component
@dash_app.callback(
    [Output('crash_table', 'data'),
     Output('statistics_table', 'data'),
     Output(component_id='crash_map', component_property='figure'),
     Output(component_id='graph_viz', component_property='figure')],
    [Input(component_id='select_year', component_property='value'),
     Input('severity-input', 'value'),
     Input('select_local_authority', 'value'),
     Input('crash_map', 'clickData'),
     Input('crash_map', 'relayoutData'),
     Input('graph_x_select', 'value'),
     Input('graph_y_select', 'value'),
     ]
)
def update_map(year_selected, severity, local_auth_selected, marker_selection, relayoutData, graph_x_select, graph_y_select):
    global accident_df, lat_min, lat_max, lon_min, lon_max
    map_fig = dash.no_update
    crash_data = dash.no_update
    stats_data = dash.no_update
    graph_fig = dash.no_update
    # lat_min = accident_df['latitude'].min()
    # lat_max = accident_df['latitude'].max()
    # lon_min = accident_df['longitude'].min()
    # lon_max = accident_df['longitude'].max()

    redraw_map = False
    redraw_graph = False
    triggered_id = callback_context.triggered[0]['prop_id']

    if triggered_id in ['crash_map.relayoutData']:
        geo_data = display_relayout_data(relayoutData)
        if len(geo_data) == 4:
            lat_min, lat_max, lon_min, lon_max = geo_data

    if year_selected is not None and len(severity) > 0:
        if triggered_id in ['select_year.value', 'severity-input.value', 'select_local_authority.value']:
            redraw_map = True

    if graph_y_select is not None and graph_x_select is not None:
        redraw_graph = True

    if triggered_id in ['crash_map.clickData']:
        crash_data = update_accident_table(marker_selection)

    accident_df_copy = apply_map_fitlers(year_selected, severity, local_auth_selected, lat_min, lat_max, lon_min, lon_max)

    print(f'Min Lat: {lat_min}, Max Lat: {lat_max}, Min Lon:{lon_min}, Max Lon: {lon_max}')


    stats_data = get_crash_statistics(accident_df_copy)

    if redraw_graph:
        graph_fig = utils.get_graph_fig(accident_df_copy, graph_x_select, graph_y_select)

    if redraw_map:
        zoom_center = utils.zoom_center(accident_df_copy['longitude'], accident_df_copy['latitude'])
        map_fig = utils.getmapfigure(accident_df_copy, zoom_center[1]['lat'], zoom_center[1]['lon'], zoom_center[0])
    return crash_data, stats_data, map_fig, graph_fig


def apply_map_fitlers(year, severities, local_auth_selected, lat_min, lat_max, lon_min, lon_max):

    global accident_df
    accident_df = utils.getaccidentdf(year)
    print(f'Shape before filering: {accident_df.shape}')
    accident_df_copy = accident_df[accident_df['accident_severity'].isin(severities)].copy()
    if len(local_auth_selected) > 0:
        accident_df_copy = accident_df_copy[accident_df['local_authority_district'].isin(local_auth_selected)].copy()

    accident_df_copy = accident_df_copy[
        accident_df_copy['latitude'].between(lat_min, lat_max) & accident_df_copy['longitude'].between(lon_min,
                                                                                                         lon_max)].copy()
    print(f'Shape after filering: {accident_df_copy.shape}')

    return accident_df_copy


def update_accident_table(selection):
    if selection is not None:
        global accident_df
        accident_index = selection["points"][0]["customdata"][0]
        accident_data = accident_df[accident_df['accident_index'] == accident_index].copy()

        if len(accident_data['accident_index']) > 0:

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
                            labels.append(i.replace('_', ' ').capitalize())
                            values.append(lookup[value])
                        elif isinstance(value, str) and value in lookup:
                            labels.append(i.replace('_', ' ').capitalize())
                            values.append(lookup[value])
                        elif isinstance(value, int) and value == -1:
                            labels.append(i.replace('_', ' ').capitalize())
                            values.append('Data missing or out of range')
                        else:
                            print(
                                f' Could not find value: {value}, type: {type(value)} in lookup: {lookup} for key: {i}')
                    else:
                        print(f'No values for label: {i}, dataframe shape: {accident_data.shape}')
                else:
                    labels.append(i.replace('_', ' ').capitalize())
                    values.append(accident_data[i])

            DF_SIMPLE = pd.DataFrame({
                'labels': labels,
                'values': values
            })
            return DF_SIMPLE.to_dict('records')
        else:
            print(f'Failed to find accident index: {accident_index} in accident data: {accident_df.head()}')
    return []


# def vehicle_data(accident_index):
def display_relayout_data(relayoutData):
    try:
        coords = relayoutData['mapbox._derived']['coordinates']
        lon_min = coords[0][0]
        lon_max = coords[1][0]
        lat_min = coords[2][1]
        lat_max = coords[1][1]

        return [lat_min, lat_max, lon_min, lon_max]
    except:
        return []


def get_crash_statistics(accident_stats_df):

    labels = ['Number of Fatal Accidents:', 'Number of Serious Accidents:', 'Number of Slight  Accidents:']
    values = [len(accident_stats_df[accident_stats_df['accident_severity'] == 1]),
              len(accident_stats_df[accident_stats_df['accident_severity'] == 2]),
              len(accident_stats_df[accident_stats_df['accident_severity'] == 3])]

    DF_SIMPLE = pd.DataFrame({
        'labels': labels,
        'values': values
    })
    return DF_SIMPLE.to_dict('records')


if __name__ == '__main__':
    dash_app.run_server(debug=True)
