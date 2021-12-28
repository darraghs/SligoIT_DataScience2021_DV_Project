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
