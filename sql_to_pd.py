import numpy as np

import sqlfile
import pandas as pd
import datetime
from datetime import datetime, date, timedelta
from matplotlib import pyplot
from matplotlib import dates
import gc


def run_query():
    db_connection = sqlfile.create_db_connection()

    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP, WC, Gust, Rain_Rate, ' \
            'Rain_Change FROM OneMonth ORDER BY Date ASC'
    df = pd.read_sql_query(query, db_connection)  # df has all days all measures
    return df


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{jj}', str(t.day) + suffix(t.day))


def get_yesterday_data():
    """

    Returns:
        max_temp
        min_temp
        max_hi
        min_wc
        rain inches

    """
    df = run_query()
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())

    # df yesterday midnight to now, yesterday plus today so far NOT PLOTED
    df_2 = (df[df['Date'] >= (yesterday_midnight)])
    # df yesterday midnight to today midnight , so 'yesterday'
    df_3 = (df_2[df_2['Date'] <= (today_midnight)])
    max_temp = df_3['Temp'].max()
    min_temp = df_3['Temp'].min()
    max_hi = df_3['HI'].max()
    return max_temp, min_temp, max_hi


def get_year_data():
    db_connection = sqlfile.create_db_connection()

    query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021'
    result = sqlfile.read_query(db_connection, query)
    # result is all temperature for the year to date
    dict_result = {
        'time': [],
        'temp': []
    }
    for record in result:
        dict_result['time'].append(record[0])
        dict_result['temp'].append(((record[1])*9/5)+32)
    for element in dict_result:
        dict_result[element] = np.array(dict_result[element])
    # print(dict_result)
    max_temp_for_year = np.amax(dict_result['temp'])  # find max temperature
    index_max_temp_for_year = np.where(dict_result['temp'] == np.amax(dict_result['temp']))  # find index of max temperatures

    date_max_temp = datetime.date(dict_result['time'][index_max_temp_for_year[0][-1]])  # use index to find date for max temperature

    min_temp_for_year = np.amin(dict_result['temp'])  # find min temperature
    index_min_temp_for_year = np.where(dict_result['temp'] == np.amin(dict_result['temp']))  # find index of min temperatures
    date_min_temp = datetime.date(dict_result['time'][index_min_temp_for_year[0][-1]])  # use index to find date of minimum temperature

    custom_date_max_temp = (custom_strftime('%A, %B {jj}', date_max_temp))  # make custom date string
    custom_date_min_temp = (custom_strftime('%A, %B {jj}', date_min_temp))

    # print(custom_date_min_temp)

   # print(f"The high temperature for the year so far was {max_temp_for_year:.1f}\u2109 on {custom_date_max_temp}.")
  # print(f"The low temperature for the year so far was {min_temp_for_year:.1f}\u2109 on {custom_date_min_temp}.")

    return max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp


def get_last_month_data(month):
    db_connection = sqlfile.create_db_connection()

    month_num = month
    query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021 and Month(TimeStamp) = ' + str(
        month_num)
    result = sqlfile.read_query(db_connection, query)
    # result is all temperature for the year to date
    dict_result = {
        'time': [],
        'temp': []
    }
    for record in result:
        dict_result['time'].append(record[0])
        dict_result['temp'].append(((record[1]) * 9 / 5) + 32)
    for element in dict_result:
        dict_result[element] = np.array(dict_result[element])
    # print(dict_result)
    max_temp_for_month = np.amax(dict_result['temp'])  # find max temperature
    index_max_temp_for_month = np.where(dict_result['temp'] == np.amax(
        dict_result['temp']))  # find index of max temperatures
    # print('Returned tuple of index_max_temp_for_year :', index_max_temp_for_year)
    # print('List of Indices of maximum element :', index_max_temp_for_year[0])
    # print(dict_result['temp'][index_max_temp_for_year[0][-1]])
    # print(dict_result['time'][index_max_temp_for_year[0][-1]])
    # print(datetime.date(dict_result['time'][index_max_temp_for_year[0][-1]]))
    date_max_temp = datetime.date(dict_result['time'][
                                      index_max_temp_for_month[0][
                                          -1]])  # use index to find date for max temperature

    min_temp_for_month = np.amin(dict_result['temp'])  # find min temperature
    index_min_temp_for_month = np.where(dict_result['temp'] == np.amin(
        dict_result['temp']))  # find index of min temperatures
    date_min_temp = datetime.date(dict_result['time'][
                                      index_min_temp_for_month[0][
                                          -1]])  # use index to find date of minimum temperature

    custom_date_max_temp = (custom_strftime('%A, %B {jj}',
                                            date_max_temp))  # make custom date string
    custom_date_min_temp = (custom_strftime('%A, %B {jj}', date_min_temp))

    # print(custom_date_min_temp)

   # print(f"The high temperature for last month was {max_temp_for_month:.1f}\u2109 on {custom_date_max_temp}.")
   # print(f"The low temperature for last month was {min_temp_for_month:.1f}\u2109 on {custom_date_min_temp}.")

    return max_temp_for_month, custom_date_max_temp, min_temp_for_month, custom_date_min_temp


def get_last_week_data():
    db_connection = sqlfile.create_db_connection()

    # query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021'
    # month_num = month
    query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Date(Timestamp) >= CURRENT_DATE - INTERVAL 7 DAY'
    result = sqlfile.read_query(db_connection, query)
    # result is all temperature for the year to date
    dict_result = {
        'time': [],
        'temp': []
    }
    for record in result:
        dict_result['time'].append(record[0])
        dict_result['temp'].append(((record[1]) * 9 / 5) + 32)
    for element in dict_result:
        dict_result[element] = np.array(dict_result[element])
    # print(dict_result)
    max_temp_for_week = np.amax(dict_result['temp'])  # find max temperature
    index_max_temp_for_week = np.where(dict_result['temp'] == np.amax(
        dict_result['temp']))  # find index of max temperatures
    # print('Returned tuple of index_max_temp_for_year :', index_max_temp_for_year)
    # print('List of Indices of maximum element :', index_max_temp_for_year[0])
    # print(dict_result['temp'][index_max_temp_for_year[0][-1]])
    # print(dict_result['time'][index_max_temp_for_year[0][-1]])
    # print(datetime.date(dict_result['time'][index_max_temp_for_year[0][-1]]))
    date_max_temp = datetime.date(dict_result['time'][
                                      index_max_temp_for_week[0][
                                          -1]])  # use index to find date for max temperature

    min_temp_for_week = np.amin(dict_result['temp'])  # find min temperature
    index_min_temp_for_week = np.where(dict_result['temp'] == np.amin(
        dict_result['temp']))  # find index of min temperatures
    date_min_temp = datetime.date(dict_result['time'][
                                      index_min_temp_for_week[0][
                                          -1]])  # use index to find date of minimum temperature

    custom_date_max_temp = (custom_strftime('%A, %B {jj}',
                                            date_max_temp))  # make custom date string
    custom_date_min_temp = (custom_strftime('%A, %B {jj}', date_min_temp))

    # print(custom_date_min_temp)

    # print(f"The high temperature for last week was {max_temp_for_week:.1f}\u2109 on {custom_date_max_temp}.")
    # print(f"The low temperature for last week was {min_temp_for_week:.1f}\u2109 on {custom_date_min_temp}.")

    return max_temp_for_week, custom_date_max_temp, min_temp_for_week, custom_date_min_temp


def get_data():
    df = run_query()
    #df = pd.read_sql_query(query, db_connection)  # df_0 has all days all measures
    df['Rain_Sum'] = 0.0

    # df_temp = df.loc[:, ['Date', 'Temp']]  # make df_temp for temperature

    # df_hi = df.loc[:, ['Date', 'HI', 'Temp']]  # make df_hi for heat index
    df['HI'] = df['HI'].where(df['HI'] > df['Temp'])  # only if HI greater than temperature, useing 'masking'
    df['HI'] = df['HI'].where(df['Temp'] > 80.0)  # And only if temperature is greater than 80.0

    # df_humid = df.loc[:, ['Date', 'Humid']]  # make df_hi for humid

    # df_wind = df.loc[:, ['Date', 'Wind', 'Wind_Direction', 'Gust']]  # make df for
    # df_wind['Gust'] = df_wind['Gust'].where(df_wind['Gust'] > df_wind['Wind'])  # only if HI greater than temperature, useing 'masking'

    df_bp = df.loc[:, ['Date', 'BP']]  # make df for bp

    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())

    df_rain = df.loc[:, ['Date', 'Rain_Rate', 'Rain_Change']]  # ALL dates
    df_rain['Rain_Sum'] = 0.0  # add column for rain sum
    df_rain_2 = (df_rain[df_rain['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(hours=48))])  # rain past 48 hours, can use to plot rain rate
    # df_rain_3 = (df_rain_2[df_rain_2['Date'] <= (pd.to_datetime(datetime.now()) - pd.Timedelta(hours=24))])  # rain 48 - 24 hours ago  NOT PLOTED
    df_rain_4 = (df_rain[df_rain['Date'] >= (yesterday_midnight)])  #  rain yesterday midnight to now, yesterday plus today so far NOT PLOTED
    df_rain_5 = (df_rain_4[df_rain_4['Date'] <= (today_midnight)])  # rain yesterday midnight to today midnight , so 'yesterday'
    df_rain_5s = df_rain_5.copy()  # make copy so can make sum
    df_rain_5s.loc[:, 'Rain_Sum'] = (df_rain_5['Rain_Change'].cumsum() / 22.5).round(1)  # now has date, rain rate, rain change and rain sum in inches PLOT for yesterday
    df_rain_6 = (df_rain[df_rain['Date'] >= (today_midnight)])  # rain so far today
    df_rain_6s = df_rain_6.copy()
    df_rain_6s.loc[:, 'Rain_Sum'] = (df_rain_6['Rain_Change'].cumsum() / 22.5).round(1)  # PLOT for today
    df_rain_7 = (df_rain[df_rain['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(hours=24))])  # rain past 24 hours
    df_rain_7s = df_rain_7.copy()
    df_rain_7s.loc[:, 'Rain_Sum'] = (df_rain_7['Rain_Change'].cumsum() / 22.5).round(1)  # PLOT for 24 hours

    # df_rain['day'] = 0
    #print(df_rain['Date'])
    df_rain['day'] = df_rain['Date'].dt.date
    #print(df_rain['day'])
    df_rain['cs'] = df_rain.groupby(['day'])['Rain_Rate'].cumsum()
    #print(df_rain['cs'])
    # print(df_humid.head())
    # print(df_humid.info(memory_usage='deep'))
    # print(df_humid.memory_usage(deep=True))

    gc.collect()
    return df_rain_6s, df_rain_5s, df_rain_7s, df_rain_2, df_rain, df


def get_temp_data():
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT Date, Temp FROM OneMonth ORDER BY Date ASC'
    df = pd.read_sql_query(query, db_connection)
    return df


def get_all_data():
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP, WC, Gust, Rain_Rate, ' \
            'Rain_Change FROM OneMonth ORDER BY Date ASC'
    df = pd.read_sql_query(query,
                           db_connection)  # df has all days all measures
    return df


#rain_result['rain_change_all_x'] = [x if x < 100 else 0.0 for x in rain_result['rain_change_all']]


if __name__ == '__main__':
    get_data()
