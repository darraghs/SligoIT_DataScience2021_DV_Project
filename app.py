import dash
import dash_bootstrap_components as dbc
import numpy
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, \
    callback_context  # pip install dash (version 2.0.0 or higher)

from accidentdashboard import utils
from accidentdashboard.data_lookup import accident_data_lookup
from accidentdashboard.layout import bootstrap_rows

accident_df = utils.getaccidentdf(2020)

app = Dash("UK Accident Dashboard", external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname='/dav2021/')

server = app.server

app.layout = dbc.Container(
    bootstrap_rows.get_bootstrap_rows(accident_df), fluid=True
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


        triggered_id = callback_context.triggered[0]['prop_id']
        if triggered_id in ['select_year.value', 'severity-input.value', 'select_local_authority.value']:
            fig = apply_map_fitlers(year_selected, severity, local_auth_selected, False)
            return [], fig
        else:
            return update_accident_table(marker_selection), dash.no_update
    return dash.no_update, dash.no_update


def apply_map_fitlers(year, severities, local_auth_selected, reset_zoom=False):
    global accident_df
    accident_df = utils.getaccidentdf(year)
    print(f'Shape before filering: {accident_df.shape}')
    accident_df = accident_df[accident_df['accident_severity'].isin(severities)].copy()
    if len(local_auth_selected) > 0:
        accident_df = accident_df[accident_df['local_authority_district'].isin(local_auth_selected)].copy()
    print(f'Shape after filering: {accident_df.shape}')

    zoom_center = utils.utils.zoom_center(accident_df['longitude'], accident_df['latitude'])
    fig = figure=utils.getmapfigure(accident_df, zoom_center[1]['lat'], zoom_center[1]['lon'], zoom_center[0])
    return fig


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
                            print(f' Could not find value: {value}, type: {type(value)} in lookup: {lookup} for key: {i}')
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


@app.callback(
    Output('Coordinates', 'children'),
    Input('crash_map', 'relayoutData'))
def display_relayout_data(relayoutData):
    try:
        print(f'Map Data: {relayoutData}')
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
