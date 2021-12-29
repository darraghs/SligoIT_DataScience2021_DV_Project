import pandas as pd
import plotly.express as px


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


def getmapfigure(accident_df):
    if accident_df is not None:
        crash_colours = ['yellow', 'orange', 'red']

        token = open(".mapbox_token").read()
        accident_df['accident_severity'] = accident_df['accident_severity'].astype(str)
        fig = px.scatter_mapbox(accident_df, lat="latitude", lon="longitude", hover_name="accident_severity",
                                hover_data=["speed_limit", "number_of_vehicles"],
                                custom_data=['accident_index'],
                                color="accident_severity",
                                color_discrete_sequence=crash_colours,
                                zoom=5, height=800)

        fig.update_layout(mapbox_style="open-street-map", mapbox_accesstoken=token)
        fig.update_mapboxes(center_lat=55, center_lon=-3.5)
        fig.update_layout(margin={"r": 1, "t": 1, "l": 1, "b": 1})
        return fig
    return {}
