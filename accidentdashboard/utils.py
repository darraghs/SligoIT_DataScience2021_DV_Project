import pandas as pd
import numpy as np
import plotly.express as px
from re import sub

from accidentdashboard.data_lookup import accident_data_lookup


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



def getaccidentdf(year):
    csvfile = f"data/dft-road-casualty-statistics-accident-{year}.csv"
    print(f'Getting CSV File: {csvfile}')
    accident_df = pd.read_csv(csvfile)
    cleanDF(accident_df)
    return accident_df


def getvehicledf(year):
    csvfile = f"data/dft-road-casualty-statistics-vehicle-${year}.csv"
    print(f'Getting CSV File: {csvfile}')
    vehicledf = pd.read_csv(csvfile)
    cleanDF(vehicledf)
    return vehicledf


def getmapfigure(accident_df, lat=55.61817975121974, lon=-3.4849391102729896, zoom=4.722400193392954, reset_zoom=False):
    token = open(".mapbox_token").read()
    if accident_df is not None:
        crash_colours = ['yellow', 'orange', 'red']
        accident_df['accident_severity'] = accident_df['accident_severity'].astype(str)
        fig = px.scatter_mapbox(accident_df, lat="latitude", lon="longitude", hover_name="accident_severity",
                                hover_data=["speed_limit", "number_of_vehicles"],
                                custom_data=['accident_index'],
                                color="accident_severity",
                                color_discrete_sequence=crash_colours,
                                zoom=zoom, height=800,

                                )

        fig.update_layout(mapbox_style="open-street-map", mapbox_accesstoken=token)
        fig.update_layout(showlegend=False)
        fig.update_layout()
        fig.update_mapboxes(center_lat=lat, center_lon=lon)
        fig.update_layout(margin={"r": 1, "t": 1, "l": 1, "b": 1})
        return fig
    else:
        fig = px.scatter_mapbox(data_frame=None, zoom=zoom, height=800)
        fig.update_layout(mapbox_style="open-street-map", mapbox_accesstoken=token)
        fig.update_layout(showlegend=False)
        fig.update_mapboxes(center_lat=lat, center_lon=lon)
        fig.update_layout(margin={"r": 1, "t": 1, "l": 1, "b": 1})
        return fig



# Take from https://stackoverflow.com/questions/63787612/plotly-automatic-zooming-for-mapbox-maps
def zoom_center(lons: tuple=None, lats: tuple=None,
                format: str='lonlat', projection: str='mercator',
                width_to_height: float=2.0) -> (float, dict):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434

    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.

    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys
    """
    if lons is None and lats is None:
        raise ValueError(
            'Must pass lons & lats'
        )

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        'lon': round((maxlon + minlon) / 2, 6),
        'lat': round((maxlat + minlat) / 2, 6)
    }

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
        0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
        0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
        47.5136, 98.304, 190.0544, 360.0
    ])

    if projection == 'mercator':
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f'{projection} projection is not implemented'
        )

    return zoom, center

# From https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-96.php
def camel_case(s):
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])

def get_graph_fig(accident_stats_df, x_axis, key):

    print(f' X-Axis: {x_axis}, key: {key}')
    if type(x_axis) == 'str' and type(key) == 'str':

        graph_df = accident_stats_df[[x_axis, key]].sort_values(by=[x_axis, key])

        for i in graph_df:
            if i in accident_data_lookup.accident_data_lookup.keys():
                lookup = accident_data_lookup.accident_data_lookup[i]
                value = graph_df[i].values[0]
                if value in lookup:
                    graph_df[i].replace(accident_data_lookup.accident_data_lookup[i], inplace=True)

        fig = px.histogram(graph_df, x=x_axis, color=key)
        return fig
