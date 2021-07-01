""" This will communicate with Mosquitto,
 main and short datatable
"""
import calendar
import gc
import time
import traceback
from datetime import date
from datetime import datetime
from datetime import timedelta
# from datetime import time
from calendar import monthrange
# import
from calendar import month_name
from calendar import month

import numpy as np
import paho.mqtt.client as mqtt
from matplotlib import dates
from matplotlib import pyplot

import sqlfile
import twitterBot
from WeatherAppLog import get_a_logger
from python_config import read_config
from send_email import read_text_to_email
from send_email import send_email
from send_email import write_text_to_send
from send_email import send_blog

logger = get_a_logger(__name__)
logger.setLevel('INFO')


def on_log(level, buff):
    """

    Args:
        client ():
        userdata ():
        level ():
        buff ():
    """
    print(level)
    print(buff)


def on_message(self, userdata, message):
    """
    This function triggered when MQTT message received,
    it will parse it into a list of data and
    sends data_list to be writen to DB

    :param self:
    :type self:
    :param userdata: not used
    :type userdata:
    :param message: the message string from Mosquitto MQTT
    :type message: str
    """
    logger.debug("START on_message() ..........")
    full_payload = message.payload.decode()
    logger.debug(f"message payload: {full_payload}")
    index = full_payload.index("MQTT")
    data_string = full_payload[index + 18:-2]  # trim to just the data string
    data_list = data_string.split(',')  # split the string to a list

    logger.debug("on_message() calls validate_input()")
    if validate_input(data_list):
        logger.debug("on_message() calls write_to_data()")
        write_to_data(data_list)
        logger.debug(
            f"data list to send to database: \n\t{data_list}\n\tmiddle of on_message")
    # make_figures()
    logger.debug(
        "END of on_message() ____________________________________________________________")


def validate_input(data_list):
    """

    Args:
        data_list ():

    Returns:

    """
    logger.debug("validate_input started")
    temperature = data_list[0]
    pressure = data_list[2]
    valid = True
    try:
        if float(temperature) < -30.0 or float(temperature) > 50.0:
            valid = False
            raise ValueError("Temperature is out of range, ")
    except ValueError as v_e:
        logger.error(f"{v_e}\n\t Temp was: {temperature}")
        send_email(subject="ERROR",
                   message=f"{v_e}\n\t Temp was: {temperature}")
    try:
        if float(pressure) < 90000 or float(pressure) > 119000:
            valid = False
            raise ValueError("pressure is out of range, ")
    except ValueError as v_e:
        logger.error(f"{v_e}\n\t pressure was: {pressure}")
        send_email(subject="ERROR",
                   message=f"{v_e}\n\t pressure was: {pressure}")
    logger.debug("end validate_data()")
    return valid


def mqtt_client():
    """
    make mqtt_client, connect to mqtt, start mqtt loop
    """
    logger.debug(
        "Start in mqtt_client()\n *********************************************************")
    mqtt_config = read_config(section='mqtt')
    broker_url = mqtt_config['broker_url']
    logger.info(f"MQTT broker url: {broker_url}")
    broker_port = int(mqtt_config['broker_port'])
    logger.info(f"MQTT broker port: {broker_port}")
    try:
        client = mqtt.Client(client_id=mqtt_config['mqtt_client_id'],
                             clean_session=False, userdata=None,
                             transport='tcp')
        logger.debug(
            f"mqtt client created: id {mqtt_config['mqtt_client_id']}")
    except Exception as ex:
        logger.exception(ex)
        send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.on_message = on_message

    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect

    tryagain = 3
    trynum = 0

    while trynum <= tryagain:

        try:
            client.connect(broker_url, broker_port)
            logger.debug("mqtt client connected")
            trynum = 4
        except OSError as ose:
            trynum += 1
            logger.error(
                f"OS Error, check url or port, {ose}/n/t with url {broker_url} and port {broker_port}")
            send_email(subject="ERROR",
                       message=f"OS Error, check url or port, {ose}")
        except Exception as ex:
            trynum += 1
            logger.exception(ex)
            send_email(subject="ERROR", message=f"The error is: {ex}.")
    try:
        client.subscribe(mqtt_config['topic'], qos=2)
        logger.debug(f"mqtt subscribed to {mqtt_config['topic']}")
    except Exception as ex:
        logger.exception(ex)
        send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.loop_start()
    logger.debug(
        "end of mqtt_client()\n ____________________________________________________________")


def on_connect(self, userdata, flags, r_c):
    logger.debug("START on_connect()")
    mqtt_config = read_config(section='mqtt')
    print(f"Connected to mosquitto {r_c} \n\twith client_id: {mqtt_config['mqtt_client_id']}.")
    logger.debug(
        f"Connected to mosquitto {r_c} \n\twith client_id: {mqtt_config['mqtt_client_id']}.")


def on_disconnect(self, userdata, r_c):
    logger.debug(f"MQTT disconnected with rc {r_c}")


def on_subscribe(self, userdata, mid, granted_qos):
    mqtt_config = read_config(section='mqtt')
    logger.debug(
        f"subscribed , with mid:{mid} and granted qos: {granted_qos} \n\tto "
        f"topic: {mqtt_config['topic']}.")


def write_to_data(list_to_write):
    """
    Writes a list of data to a SQL table. The SQL table name
    and other info comes from config.ini, sedtion: sqltable.
    Args:
        list_to_write: type, list. a list of data to write to SQL

    Returns:
        None

    """
    logger.debug("start write_to_data()")
    logger.debug("write_to_data() call to read_config()")
    database_table_t = read_config(section='sqltable')
    database_table = database_table_t['database_table']

    db_connection = sqlfile.create_db_connection()

    device_id = 6
    try:
        query = 'INSERT INTO ' + database_table + (
                ' (timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity,'
                'Barometric_Pressure, Current_Wind_Speed, Current_Wind_Gust, '
                'Current_Wind_Direction, Wind_Speed_Maximum, '
                'Wind_Gust_Maximum, OurWeather_DateTime, Lightning_Time, '
                'Lightning_Distance, Lightning_Count, Rain_Total ) '
                'VALUES (CURRENT_TIMESTAMP, %i, %.3f, %.3f, %.3f, %.3f, %.3f, '
                '%.3f, %.3f, %.3f, "%s", "%s", %i, %i, %.2f)' % (
                    int(device_id), float(list_to_write[0]),
                    float(list_to_write[1]), float(list_to_write[2]),
                    float(list_to_write[3]), float(list_to_write[4]),
                    float(list_to_write[5]), float(list_to_write[7]),
                    float(list_to_write[8]), list_to_write[9],
                    list_to_write[10], int(list_to_write[11]),
                    int(list_to_write[12]), float(list_to_write[6])))

        sqlfile.execute_query(db_connection, query)
        sqlfile.close_db_connection(db_connection)

    except IndexError as i_e:
        logger.error(
            f"failed to build query to write to database,\n\tlength should be "
            f"14; {len(list_to_write)}\n\tlist to write: {list_to_write}\n\t"
            f"Error: {i_e}")
        send_email(subject="ERROR", message=f"The error is: {i_e}.")

    # sqlfile.execute_query(db_connection, query)
    # sqlfile.close_db_connection(db_connection)
    logger.debug("end write_to_data()")


def clean_hi(hi_result):

    # convert into a np array
    for element in hi_result:
        hi_result[element] = np.array(hi_result[element])

    hi_result['heat_index'] = hi_result['heat_index'][
        hi_result['temp'] > 80]  # filter heat_index for temp > 80
    hi_result['heat_index_temp'] = hi_result['temp'][hi_result['temp'] > 80]

    hi_result['time_heat_index'] = hi_result['time_heat_index'][
        hi_result['temp'] > 80]
    hi_result['time_heat_index'] = hi_result['time_heat_index'][
        hi_result['heat_index'] > hi_result['heat_index_temp']]

    hi_result['heat_index'] = hi_result['heat_index'][
        hi_result['heat_index'] > hi_result[
            'heat_index_temp']]  # to filter out heat index less than temp
    del hi_result['heat_index_temp']

    return hi_result


def clean_wc(wc_result):
    for element in wc_result:
        wc_result[element] = np.array(wc_result[element])
    wc_result['wind_chill'] = wc_result['wind_chill'][wc_result['temp'] < 50]
    wc_result['time_wind_chill'] = wc_result['time_wind_chill'][
        wc_result['temp'] < 50]
    wc_result['wind_for_wc'] = wc_result['wind_for_wc'][wc_result['temp'] < 50]
    wc_result['wind_chill'] = wc_result['wind_chill'][
        wc_result['wind_for_wc'] > 3]
    wc_result['time_wind_chill'] = wc_result['time_wind_chill'][
        wc_result['wind_for_wc'] > 3]
    del wc_result['temp']
    del wc_result['wind_for_wc']
    return wc_result


def clean_rain(rain_result):
    # TODO try enumerate
    # for index in range(len(rain_result['rain_rate'])):  # clean none to 0.0

    for index, result in enumerate(rain_result['rain_rate'], 0):

    #    if rain_result['rain_rate'][index] is None:
    #        rain_result['rain_rate'][index] = 0.0
        rain_result['rain_rate'][index] = 0.0 if rain_result['rain_rate'][index] is None else rain_result['rain_rate'][index]

    for element in rain_result:
        rain_result[element] = np.array(rain_result[element])
    # yesterday rain
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())
    # yesterday midnight to now
    rain_result['time_rain_yesterday'] = rain_result['time'][
        (rain_result['time']) > yesterday_midnight]
    rain_result['rain_change_yesterday'] = rain_result['rain_change_all'][
        (rain_result['time']) > yesterday_midnight]  # in mm
    # yesterday midnight to today midnight
    rain_result['time_rain_yesterday_filtered'] = \
        rain_result['time_rain_yesterday'][
            (rain_result['time_rain_yesterday']) < today_midnight]
    rain_result['rain_change_yesterday_filtered'] = \
        rain_result['rain_change_yesterday'][
            (rain_result['time_rain_yesterday']) < today_midnight]  # in mm
    # make cumulative sum
    rain_result['rain_total_yesterday_filtered'] = (
            np.cumsum(rain_result[
                          'rain_change_yesterday_filtered']) / 22.5)  # in INCH

    # today midnight to now
    rain_result['time_rain_today'] = rain_result['time'][
        (rain_result['time']) > today_midnight]
    rain_result['rain_change_today'] = (rain_result['rain_change_all'])[
        (rain_result['time']) > today_midnight]  # in mm
    # make cumulative sum
    rain_result['rain_total_today'] = (
            np.cumsum(rain_result['rain_change_today']) / 22.5)  # in inch
    #   print(dict_result['rain_total_today'])

    # rain 24
    time_24 = datetime.now() - timedelta(days=1)
    rain_result['time_rain_24'] = rain_result['time'][
        (rain_result['time']) > time_24]
    rain_result['rain_change_24'] = (rain_result['rain_change_all'])[
        (rain_result['time']) > time_24]  # in mm
    # make cumulative sum
    rain_result['rain_total_24'] = (
            np.cumsum(rain_result['rain_change_24']) / 22.5)  # in inch

    #  filter 30 day rain to 7 days
    rain_result['rain_7'] = rain_result['rain_30'][
        dates.date2num(rain_result['time_rain_30']) > dates.date2num(
            datetime.now()) - 7]

    i = 0
    for unit in rain_result['rain_30']:
        if unit < 0.01:
            rain_result['rain_30'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

    del rain_result['time_rain_yesterday']
    del rain_result['rain_change_yesterday']
    del rain_result['rain_total_yesterday']
    del rain_result['rain_change_today']
    del rain_result['rain_change_24']
    del rain_result['rain_change_all']
    # del rain_result['time_rain_all']
    del rain_result['rain_change_yesterday_filtered']

    return rain_result


def get_data_a():
    """
    Runs a series of SQL queries and combines into a dict
    Returns:
        dict_result: a dict type

    """
    logger.debug("START get_data_a() &&&&&&&&&&&&&")
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP, WC, Gust, Rain_Rate, ' \
            'Rain_Change FROM OneMonth ORDER BY Date ASC'
    result = sqlfile.read_query(db_connection, query)
    # QUERY FOR # 30 DAY RAIN  will 'filter' to get 7 day
    query = 'SELECT Date, SUM(Rain_Change) FROM OneMonth GROUP BY Day(Date) ORDER BY Date ASC'
    result_rain_30 = sqlfile.read_query(db_connection, query)

    sqlfile.close_db_connection(db_connection)  # close the db connection
    # Move results into dict of lists
    dict_result = {
        'time': [],
        'temp': [],
        'heat_index': [],
        'humid': [],
        'wind_speed': [],
        'wind_d': [],
        'baro_press': [],
        'time_heat_index': [],
        'time_rain_30': [],
        'rain_30': [],
        'rain_30_sum': [],
        'time_rain_yesterday': [],
        'rain_change_yesterday': [],
        'rain_total_yesterday': [],
        'time_rain_bar': [],
        'rain_change_bar': [],
        'time_rain_today': [],
        'rain_change_today': [],
        'rain_total_today': [],
        'time_rain_24': [],
        'rain_change_24': [],
        'rain_total_24': [],
        'rain_7': [],
        'wind_chill': [],
        'time_wind_chill': [],
        'wind_for_wc': [],
        'gust': [],
        'rain_rate': [],
        'rain_change_all': [],
        # 'time_rain_all': [],
        'time_rain_yesterday_filtered': [],
        'rain_change_yesterday_filtered': [],
        'rain_total_yesterday_filtered': []
    }

    hi_result = {
        'heat_index': [],
        'temp': [],
        'time_heat_index': [],
        'heat_index_temp': []
    }

    wc_result = {
        'wind_chill': [],
        'time_wind_chill': [],
        'wind_for_wc': [],
        'temp': []
    }

    rain_result = {
        'time_rain_yesterday_filtered': [],
        'time_rain_today': [],
        'time_rain_24': [],
        'rain_total_yesterday': [],
        'rain_total_yesterday_filtered': [],
        'rain_total_today': [],
        'rain_total_24': [],
        'rain_rate': [],
        'rain_change_all': [],
        'time': [],
        'time_rain_30': [],
        'rain_30': [],
        'rain_30_sum': [],
        'rain_7': []
    }

    for record in result:  # make a list for each measure
        dict_result['time'].append(record[0])
        dict_result['temp'].append(record[1])
        dict_result['humid'].append(record[3])
        dict_result['wind_speed'].append(record[4])
        dict_result['wind_d'].append(record[5])
        dict_result['baro_press'].append(record[6])
        # dict_result['time_heat_index'].append(record[0])
        # dict_result['wind_chill'].append(record[7])
        # dict_result['time_wind_chill'].append(record[0])
        # dict_result['wind_for_wc'].append(record[4])
        dict_result['gust'].append(record[8])

        rain_result['rain_rate'].append(record[9])
        rain_result['rain_change_all'].append(record[10])  # in mm
        rain_result['time'].append(record[0])

        hi_result['heat_index'].append(record[2])
        hi_result['temp'].append(record[1])
        hi_result['time_heat_index'].append(record[0])
        hi_result['heat_index_temp'].append(record[1])

        wc_result['wind_chill'].append(record[7])
        wc_result['time_wind_chill'].append(record[0])
        wc_result['wind_for_wc'].append(record[4])
        wc_result['temp'].append(record[1])

    # TODO try enumerate
    # for index in range(len(rain_result['rain_rate'])):  # clean none to 0.0
    # if rain_result['rain_rate'][index] is None:
    # rain_result['rain_rate'][index] = 0.0

    if len(result_rain_30) > 0:
        for record in result_rain_30:
            rain_result['time_rain_30'].append(record[0])
            try:
                rain_result['rain_30'].append(record[1] / 22.5)
            except TypeError as tee:
                logger.error(f"type error {tee}\n\t {record}")
                rain_result['rain_30'].append(0)
            rain_result['rain_30_sum'].append(sum(rain_result['rain_30']))
    else:
        rain_result['time_rain_30'].append(0)
        rain_result['rain_30'].append(0)
        rain_result['rain_30_sum'].append(0)

    #    convert each list to a numpy array
    for element in dict_result:
        dict_result[element] = np.array(dict_result[element])

    hi_result = clean_hi(hi_result)

    wc_result = clean_wc(wc_result)

    rain_result = clean_rain(rain_result)

    gc.collect()

    dict_clean = clean_dict(dict_result)
    logger.debug("END get_data() .....")
    return dict_clean, hi_result, wc_result, rain_result


def clean_dict(dict_result):
    logger.debug("START clean_dict() started")
    del dict_result['time_rain_yesterday']
    del dict_result['rain_change_yesterday']
    del dict_result['rain_total_yesterday']
    del dict_result['rain_change_today']
    del dict_result['rain_change_24']
    del dict_result['rain_change_all']
    #  del dict_result['time_rain_all']
    del dict_result['rain_change_yesterday_filtered']

    return dict_result


def fig_1_rain(rain_dict, ax4):
    if len(rain_dict['rain_total_today']) > 0:  # today
        logger.debug(f"Rain today: {rain_dict['rain_total_today']}")
        ax4.plot(rain_dict['time_rain_today'], rain_dict['rain_total_today'],
                 marker='o',
                 linestyle='--', color='green', markersize=1, linewidth=2,
                 label=f"Rain {rain_dict['rain_total_today'][-1]:.1f} inches today")
    else:
        rain_dict['rain_total_today'] = [0.0,
                                         0.0]  # if nothing in rain today then set a 0.0
        logger.debug("rain today set to 0 because len was 0")

    if len(rain_dict['rain_total_yesterday_filtered']) > 0:  # yesterday
        logger.debug(
            f"rain yesterday : {rain_dict['rain_total_yesterday_filtered']}")
        ax4.plot(rain_dict['time_rain_yesterday_filtered'],
                 rain_dict['rain_total_yesterday_filtered'], marker='o',
                 linestyle='--',
                 color='orange', markersize=1, linewidth=2,
                 label=f"Rain {rain_dict['rain_total_yesterday_filtered'][-1]:.1f} in yesterday")
    else:
        rain_dict['rain_total_yesterday_filtered'] = [0, 0]
    if len(rain_dict['rain_total_24']) > 0:  # 24
        ax4.plot(rain_dict['time_rain_24'], rain_dict['rain_total_24'],
                 marker='o', linestyle='-',
                 color='blue', markersize=1, linewidth=1,
                 label=f"Rain {rain_dict['rain_total_24'][-1]:.1f} inches in 24 hours")
    else:
        rain_dict['rain_total_24'] = [0, 0]
    if len(rain_dict['rain_rate']) > 0:
        ax4.plot(rain_dict['time'], rain_dict['rain_rate'], marker='s',
                 linestyle='', color='blue',
                 markersize=4, linewidth=1, label="Rain Rate, inch / hr")

    ax4.axis(ymin=0, ymax=((max(max(rain_dict['rain_total_24']),
                                max(rain_dict['rain_total_today']),
                                max(rain_dict[
                                        'rain_total_yesterday_filtered']))) + 1) // 1,
             xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))

    return ax4


def make_fig_1(ax_dict, hi_dict, wc_dict, rain_dict):
    compass = {
        0.0: 'North',
        22.5: 'North',
        45: 'Northeast',
        67.5: 'East',
        90: 'East',
        112.5: 'East',
        135: 'Southeast',
        157.5: 'South',
        180: 'South',
        202.5: 'South',
        225: 'Southwest',
        247.5: 'West',
        270: 'West',
        292.5: 'West',
        315: 'Northwest',
        337.5: 'North',
        360: 'North',
    }

    # figure
    figure_1 = pyplot.figure(num='one', facecolor='green',
                             figsize=(18.9, 10.4))
    # pyplot.xticks(fontsize=16)

    pyplot.suptitle(f"One Day Graph: {datetime.today().date()}", fontsize='15', fontweight='bold')
    gs = figure_1.add_gridspec(10, 5)

    #  day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 1]

    try:
        max_temp = max(
            ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
                datetime.now()) - 1])
        min_temp = min(
            ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
                datetime.now()) - 1])
    except ValueError:
        #    logger.error(
        #        f"Value Error: {vee}\n\tno data in ax_temp so will set max_temp and min_temp to 0")
        max_temp = 0
        min_temp = 0
        # send_email(subject="ERROR", message=f"The error is: {ve}.")

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline

    # ax1  TEMP
    ax1 = figure_1.add_subplot(gs[:5, :4])
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='',
             color='black', markersize=2.0,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n(High: {max_temp} Low: {min_temp}) ")

    if len(hi_dict['heat_index']) > 0 and \
            dates.date2num(hi_dict['time_heat_index'][-1]) > (
            dates.date2num(datetime.now())) - 1:
        hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (dates.date2num(datetime.now())) - 1]

        ax1.plot(hi_dict['time_heat_index'], hi_dict['heat_index'], marker=6,
                 linestyle='', color='red', label=f'Heat Index Max {max(hi)}\u2109', markersize=5)

    # if ax_dict['humid'] is not None:
    ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='',
             color='orange',
             label=f"Humidity {ax_dict['humid'][-1]:.0f}%")
    # try:
    if len(wc_dict['wind_chill']) >= 1 and dates.date2num(
            wc_dict['time_wind_chill'][-1]) > (
            dates.date2num(datetime.now())) - 1:
        ax1.plot(wc_dict['time_wind_chill'], wc_dict['wind_chill'],
                 marker='v', linestyle='', color='blue',
                 label='Wind chill')
    # except IndexError as iee:
    #     logger.error(f"failed to plot wind chill Error: {iee}")

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours

    style_ax1(ax1)
    ax1.xaxis.set_major_locator(dates.HourLocator(interval=6))

    # logger.debug('did make_ax1 in figure 1')

    # ax2  WIND
    # gust period

    #   gust_period = ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(
    #    datetime.now()) - 0.25]
    try:
        max_gust = max(
            ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(
                datetime.now()) - 0.5])
    except ValueError as vee:
        logger.error(
            f"Value Error: {vee}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
    # send_email(subject="ERROR",
    #            message=f"The error is: {ve}. There is no data in the ax_dict['gust'] so is ste "
    #                    f"to 0 for fig 1.")

    ax2 = figure_1.add_subplot(gs[6:8, :4])

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='-',
             color='black',
             markersize=2, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \n from the "
                   f"{compass[ax_dict['wind_d'][-1]]}\n gusting between \n{ax_dict['gust'][-1]:.0f}"
                   f" and {max_gust:.0f} MPH")

    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours

    style_ax2(ax2)
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))

    # ax3  BP
    ax3 = figure_1.add_subplot(gs[8:, :4])
    # ax3 is local scope but modifies fig that was passed in as argument
    #  pyplot.xticks([], rotation='45')
    #
    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='',
             color='green',
             markersize=2.0, linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours
    #  ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))

    style_ax3(ax3)
#    ax3.xticks(fontsize=16)
#    ax3.xlabel(fontdict={'size': 16})
    ax3.tick_params(axis='x', labelsize=16)
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:00'))  # '%m/%d\n%H:00'))

    ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))

    # ax4 RAIN
    ax4 = figure_1.add_subplot(gs[5:6, :4])
    #   pyplot.xticks([], rotation='45')
    #   ax4.xaxis.set_minor_locator(dates.HourLocator(interval=1))

    # if 1 day
    #  if (ax_dict['title'] == '1 day'):
    #  ax4.bar(ax_dict['time_rain_bar'], ax_dict['rain_change_bar'], color='red', width=0.005,
    #  label="wwww")
    ax4 = fig_1_rain(rain_dict, ax4)

    #  ax4.set_title('', fontsize='15')
    #   ax4.set_xlabel('')
    #   ax4.set_ylabel("inches")
    #   ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    #   ax4.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    #   ax4.grid(True, which='both', axis='both')

    #   ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True,
    #              ncol=1, fontsize=15)
    #   ax4.set_facecolor('#edf7f7')

    style_ax4(ax4)
    ax4.xaxis.set_major_locator(dates.HourLocator(interval=6))

    pyplot.savefig(fname="./figures/fig_1.jpeg", format='jpeg')

    #     mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def make_fig_2(ax_dict, rain_dict, hi_dict, wc_dict):
    compass = {
        0.0: 'North',
        22.5: 'North',
        45: 'Northeast',
        67.5: 'East',
        90: 'East',
        112.5: 'East',
        135: 'Southeast',
        157.5: 'South',
        180: 'South',
        202.5: 'South',
        225: 'Southwest',
        247.5: 'West',
        270: 'West',
        292.5: 'West',
        315: 'Northwest',
        337.5: 'North',
        360: 'North',
    }
    figure_2 = pyplot.figure(num='two', facecolor='green',
                             figsize=(18.9, 10.4))
    pyplot.suptitle("7 Days", fontsize='15', fontweight='bold')
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    gs = figure_2.add_gridspec(10, 5)

    #   day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 7]

    try:
        max_temp = max(
            ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
                datetime.now()) - 7])
        min_temp = min(
            ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
                datetime.now()) - 7])
    except ValueError as vee:
        logger.error(
            f"Value Error: {vee}\n\tno data in day_x so will set max_temp to 0")
        max_temp = 0
        min_temp = 0

    #        send_email(subject="ERROR",
    #                   message=f"The error is: {ve}. There is no data in day_x so set to 0 for fig 2.")

    #    try:
    #        min_temp = min(day_x)
    #    except ValueError as ve:
    #        logger.error(
    #            f"Value Error: {ve}\n\tno data in day_x so will set min_temp to 0")
    #        min_temp = 0
    #        send_email(subject="ERROR",
    #                   message=f"The error is: {ve}. There is no data in day_x so set to 0 for fig 2.")
    #   min_temp = min(day_x)

    ax1 = figure_2.add_subplot(gs[:5, :4])
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='',
             color='black', markersize=1.5,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n(High: {max_temp} Low: {min_temp})")
    if len(hi_dict['heat_index']) > 0 and dates.date2num(
            hi_dict['time_heat_index'][-1]) > (
            dates.date2num(datetime.now())) - 7:
        hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (dates.date2num(datetime.now())) -7]

        ax1.plot(hi_dict['time_heat_index'], hi_dict['heat_index'], marker=6,
                 linestyle='', color='red', label=f'Heat Index Max {max(hi)}\u2109', ms=1)



#    if ax_dict['wind_chill'] is not None:
    if len(wc_dict['wind_chill']) >= 1 and dates.date2num(
            wc_dict['time_wind_chill'][-1]) > (
            dates.date2num(datetime.now())) - 1:
        ax1.plot(ax_dict['time_wind_chill'], ax_dict['wind_chill'], marker='v',
                 linestyle='', color='blue',
                 label='Wind chill', markersize='3.0')
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 7 days
    style_ax1(ax1)
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=6))

    #   logger.debug('did make_ax1 in figure 2')
    #   ax1.set_facecolor('#edf7f7')

    # ax2  WIND
    ax2 = figure_2.add_subplot(gs[6:8, :4])
    #   gust_period = ax_dict['gust'][
    #      dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 0.5]
    try:
        max_gust = max(ax_dict['gust'][
                           dates.date2num(ax_dict['time']) > dates.date2num(
                               datetime.now()) - 0.5])
    except ValueError as vee:
        logger.error(
            f"Value Error: {vee}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
    #    send_email(subject="ERROR",
    #               message=f"The error is: {ve}. There is no data ax_dict['gust'] so will be set "
    #                       f"to 0. Fig 2.")

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='',
             color='black', markersize='1.0', linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \nfrom the "
                   f"{compass[ax_dict['wind_d'][-1]]}\ngusting between \n{ax_dict['gust'][-1]:.0f} "
                   f"and {max_gust:.0f} MPH")
    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours
    style_ax2(ax2)
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=6))

    # ax3  BP
    ax3 = figure_2.add_subplot(gs[8:,
                               :4])  # ax3 is local scope but modifies fig that was passed in
    #   pyplot.xticks([], rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='',
             color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")
    ax3.axis(ymin=29.50, ymax=30.71, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours
    style_ax3(ax3)
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d'))

    # ax4 RAIN
    ax4 = figure_2.add_subplot(gs[5:6, :4])
    #   pyplot.xticks([], rotation='45')

    #    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))

    ax4.bar(rain_dict['time_rain_30'], rain_dict['rain_30'], color='blue',
            width=0.99,
            label=f"Rain {sum(rain_dict['rain_7']):0.1f} inches\n this 7 days",
            align='edge')
    ax4.axis(ymin=0, ymax=(max(rain_dict['rain_30']) + 1) // 1,
             xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))
    style_ax4(ax4)
    ax4.xaxis.set_minor_locator(dates.HourLocator(interval=6))

    pyplot.savefig(fname="./figures/fig_2.png", format='png')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def style_ax1(ax1):
    ax1.xaxis.set_major_formatter(dates.DateFormatter(''))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
               ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')
    ax1.set_facecolor('#edf7f7')
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))


def style_ax2(ax2):
    ax2.xaxis.set_major_formatter(dates.DateFormatter(''))
    ax2.set_title('', fontsize='15')
    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True,
               ncol=1, fontsize=15)
    ax2.set_xlabel('')
    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')
    ax2.set_facecolor('#edf7f7')
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=1))


def style_ax3(ax3):
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d'))
    ax3.set_title('', fontsize='15')
    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
               ncol=1, fontsize=15)
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')
    ax3.set_facecolor('#edf7f7')
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))


def style_ax4(ax4):
    ax4.xaxis.set_major_formatter(dates.DateFormatter(''))
    ax4.set_title('', fontsize='15')
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True,
               ncol=1, fontsize=15)
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(b=True, which='major', color='#666666', linewidth=1.2,
             linestyle='-', axis='both')
    ax4.grid(b=True, which='both', axis='both')
    ax4.set_facecolor('#edf7f7')
    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_minor_locator(dates.HourLocator(interval=1))


def make_fig_3(ax_dict, rain_dict, hi_dict, wc_dict):
    compass = {
        0.0: 'North',
        22.5: 'North',
        45: 'Northeast',
        67.5: 'East',
        90: 'East',
        112.5: 'East',
        135: 'Southeast',
        157.5: 'South',
        180: 'South',
        202.5: 'South',
        225: 'Southwest',
        247.5: 'West',
        270: 'West',
        292.5: 'West',
        315: 'Northwest',
        337.5: 'North',
        360: 'North',
    }
    figure_3 = pyplot.figure(num='three', facecolor='green',
                             figsize=(18.9, 10.4))
    pyplot.suptitle("30 Days", fontsize='15', fontweight='bold')
    gs = figure_3.add_gridspec(10, 5)

    #   day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 30]
    max_temp = max(
        ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
            datetime.now()) - 30])
    min_temp = min(
        ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(
            datetime.now()) - 30])
    #   print(min_temp)
    ax1 = figure_3.add_subplot(gs[:5, :4])
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)
    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='',
             color='black',
             markersize=1.0, label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n"
                                   f"(High: {max_temp} Low: {min_temp})")
    if len(hi_dict['heat_index']) > 0 and dates.date2num(
            hi_dict['time_heat_index'][-1]) > (
            dates.date2num(datetime.now())) - 30:
        hi = hi_dict['heat_index'][
            dates.date2num(hi_dict['time_heat_index']) > (
                dates.date2num(datetime.now())) - 30]

        ax1.plot(hi_dict['time_heat_index'], hi_dict['heat_index'], marker=6,
                 linestyle='', color='red',
                 label=f'Heat Index Max {max(hi)}\u2109', markersize='1')




  #  hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (dates.date2num(datetime.now())) -30]
  #  print(max(hi))
   # print(min(hi))
   # print("max")











    #    if ax_dict['humid'] is not None:
    #        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
    #                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")
#    if ax_dict['wind_chill'] is not None:
    if len(wc_dict['wind_chill']) >= 1 and dates.date2num(
            wc_dict['time_wind_chill'][-1]) > (
            dates.date2num(datetime.now())) - 30:
        ax1.plot(ax_dict['time_wind_chill'], ax_dict['wind_chill'], marker='v',
                 linestyle='', color='blue',
                 label='Wind chill', markersize='2.0')
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 7 days

    style_ax1(ax1)
    ax1.tick_params(axis='x', which='minor', bottom=False, grid_linestyle='')

    # ax2  WIND
    ax2 = figure_3.add_subplot(gs[6:8, :4])
    #   gust_period = ax_dict['gust'][
    #        dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 1]
    try:
        max_gust = max(ax_dict['gust'][
                           dates.date2num(ax_dict['time']) > dates.date2num(
                               datetime.now()) - 1])
    except ValueError as vee:
        logger.error(
            f"Value Error: {vee}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
    except Exception as ex:
        logger.error(f"{ex}")
        send_email(subject="ERROR", message=f"{ex}, Fig 3, gust")

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='',
             color='black', markersize=1.5,
             linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \nfrom the "
                   f"{compass[ax_dict['wind_d'][-1]]}\ngusting between \n{ax_dict['gust'][-1]:.0f}"
                   f" and {max_gust:.0f} MPH")

    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours

    style_ax2(ax2)
    ax2.tick_params(axis='x', which='minor', bottom=False, grid_linestyle='')

    # ax3  BP
    ax3 = figure_3.add_subplot(gs[8:,
                               :4])  # ax3 is local scope but modifies fig that was passed in
    pyplot.xticks(rotation='25')

    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='',
             color='green', markersize=1.5,
             linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71,
             xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(
                 datetime.now())))  # set a rolling x axis for preceding 24 hours
    # ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    #    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))

    style_ax3(ax3)
    ax3.tick_params(axis='x', which='minor', bottom=False, grid_linestyle='')

    # ax4 RAIN
    ax4 = figure_3.add_subplot(gs[5:6, :4])
    #   pyplot.xticks([], rotation='45')

    #   ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))

    ax4.bar(rain_dict['time_rain_30'], rain_dict['rain_30'], color='blue',
            width=0.99,
            label=f"Rain inches,\n {rain_dict['rain_30_sum'][-1]:.1f} total this 30 days",
            align='edge')
    ax4.axis(ymin=0, ymax=(max(rain_dict['rain_30']) + 1) // 1,
             xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))

    style_ax4(ax4)
    ax4.tick_params(axis='x', which='minor', bottom=False, grid_linestyle='')

    pyplot.savefig(fname="./figures/fig_3.png", format='png')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def is_new_day(day=1):
    return datetime.today().day != day


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{jj}', str(t.day) + suffix(t.day))


def end_of_day_report():
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP, WC, Gust, Rain_Rate, ' \
            'Rain_Change FROM OneMonth WHERE Day(Date) = Day(CURRENT_DATE - INTERVAL 1 Day) ORDER BY Date ASC'
    # query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021'
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
    print(dict_result)
    input('print')
    max_temp_for_year = np.amax(dict_result['temp'])  # find max temperature
    index_max_temp_for_year = np.where(dict_result['temp'] == np.amax(
        dict_result['temp']))  # find index of max temperatures
    # print('Returned tuple of index_max_temp_for_year :', index_max_temp_for_year)
    # print('List of Indices of maximum element :', index_max_temp_for_year[0])
    # print(dict_result['temp'][index_max_temp_for_year[0][-1]])
    # print(dict_result['time'][index_max_temp_for_year[0][-1]])
    # print(datetime.date(dict_result['time'][index_max_temp_for_year[0][-1]]))
    date_max_temp = datetime.date(dict_result['time'][
                                      index_max_temp_for_year[0][
                                          -1]])  # use index to find date for max temperature

    min_temp_for_year = np.amin(dict_result['temp'])  # find min temperature
    index_min_temp_for_year = np.where(dict_result['temp'] == np.amin(
        dict_result['temp']))  # find index of min temperatures
    date_min_temp = datetime.date(dict_result['time'][
                                      index_min_temp_for_year[0][
                                          -1]])  # use index to find date of minimum temperature

    custom_date_max_temp = (custom_strftime('%A, %B {jj}',
                                            date_max_temp))  # make custom date string
    custom_date_min_temp = (custom_strftime('%A, %B {jj}', date_min_temp))

    # print(f"The high temperature for the year so far was {max_temp_for_year:.1f}\u2109 on {custom_date_max_temp}.")
    # print(f"The low temperature for the year so far was {min_temp_for_year:.1f}\u2109 on {custom_date_min_temp}.")

    return max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp
    return True



def get_last_week_stats():
    db_connection = sqlfile.create_db_connection()

    # query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021'
    month_num = month
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



def get_last_month_stats(month):
    db_connection = sqlfile.create_db_connection()

    # query = 'SELECT TimeStamp, Outdoor_Temperature FROM OURWEATHERTable WHERE Year(TimeStamp) = 2021'
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


def get_year_stats():
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



def make_email_texts():
    dict_result, hi_dict, wc_result, rain_result = get_data_a()  # get data from SQL
    if True:
    # if (dict_result['time'][-1]).day != date.today().day:  # day of last entry not same as today, new day
        print('new day is true, should see daily email')
        today = date.today()
        yesterday = today - timedelta(days=1)
        yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
        temp_yesterday = []
        temp_yesterday = dict_result['temp'][
            (dict_result['time']) > yesterday_midnight]
        hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (
            dates.date2num(datetime.now())) - 1]

        max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp = get_year_stats()
        string_email = f"The high yesterday was {max(temp_yesterday)}" \
                      f" and the low was {min(temp_yesterday)} \u2109.\n" \
                      f"There was {rain_result['rain_total_yesterday_filtered'][-1]:.1f} " \
                      f"inches of rain.\n"

        if len(hi) > 0:
            string_email += f"The max heat index yesterday was {max(hi)}\u2109.\n"

        string_email += f"\nThe high temperature so far this year was {max_temp_for_year:.1f}\u2109 " \
                       f"on {custom_date_max_temp} and the low was {min_temp_for_year:.1f} on {custom_date_min_temp}.\n\n" \
                       f"Time : {datetime.now().time()}"

        subject = f"Daily weather message for {datetime.today().date()}"
        attach = './figures/fig_1.jpeg'
        write_text_to_send(string_email, file_name='daily_email.txt')

        send_email(message=read_text_to_email(file_name='daily_email.txt'),
                  subject=subject, file=attach)

        if today.day == 1:  # set as 1 for first day of month
            print('first of month is true, should see monthly email')
            # modify so is a monthly report
            # print("this is the first day of the month.")
            last_month = monthrange(today.year, today.month - 1)  # a tuple (# day of week for first day, # days)
           # print(last_month)
          #  print(today.month - 2)
           # date_obj = (datetime.strftime(today, '%B'))
           # print(date_obj)
            # print(month_name[last_month[0]])
            # print(month.)
           # dict_result['time'] = dict_result['time'][(datetime.strftime(dict_result['time'], '%m')) == 6]
          #  print(datetime.strftime(dict_result['time'][1], '%m'))
          #  print(dict_result['time'])
            max_temp_for_month, custom_date_max_temp, min_temp_for_month, custom_date_min_temp = get_last_month_stats(today.month - 1)
            string_email = f"Today is start of {calendar.month_name[today.month]}.\n\n" \
                          f"Last month the high temperature was {max_temp_for_month:.1f}\u2109 " \
                          f"on {custom_date_max_temp} and " \
                          f"the low was {min_temp_for_month:.1f} on {custom_date_min_temp}.\n\n" \
                          f"Time : {datetime.now().time()}"

            subject = f"Weather summary for {calendar.month_name[today.month - 1]}"
            attach = './figures/fig_3.png'
            write_text_to_send(string_email, file_name='monthly_email.txt')
            send_email(
                 message=read_text_to_email(file_name='monthly_email.txt'),
                 subject=subject, file=attach)

        if datetime.today().weekday() == 0:  # if today is Monday 0. sunday 7
            print('new week is true, should see weekly email')
            max_temp_for_week, custom_date_max_temp, min_temp_for_week, custom_date_min_temp = get_last_week_stats()
            string_email = f"Today is start of new week.\n\n" \
                          f"Last week the high temperature was {max_temp_for_week:.1f}\u2109 " \
                          f"on {custom_date_max_temp} and " \
                          f"the low was {min_temp_for_week:.1f} on {custom_date_min_temp}.\n\n" \
                          f"Time : {datetime.now().time()}"

            subject = 'Weekly post'
            attach = './figures/fig_2.png'
            write_text_to_send(string_email, file_name='weekly_email.txt')
            # print(string_blog)
            send_email(message=read_text_to_email(file_name='weekly_email.txt'),
                       subject=subject, file=attach)

    return True


def make_blog_posts():
    dict_result, hi_dict, wc_result, rain_result = get_data_a()  # get data from SQL
    if True:
    # if (dict_result['time'][-1]).day != date.today().day:  # day of last entry not same as today, new day
        print('new day is true, should see daily blog post')
        today = date.today()
        yesterday = today - timedelta(days=1)
        yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
        temp_yesterday = []
        temp_yesterday = dict_result['temp'][
            (dict_result['time']) > yesterday_midnight]
        hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (
            dates.date2num(datetime.now())) - 1]

        max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp = get_year_stats()
        string_blog = f"The high yesterday was {max(temp_yesterday)}" \
                      f" and the low was {min(temp_yesterday)} \u2109.\n" \
                      f"There was {rain_result['rain_total_yesterday_filtered'][-1]:.1f} " \
                      f"inches of rain.\n"

        if len(hi) > 0:
            string_blog += f"The max heat index yesterday was {max(hi)}\u2109.\n"

        string_blog += f"\nThe high temperature so far this year was {max_temp_for_year:.1f}\u2109 " \
                       f"on {custom_date_max_temp} and the low was {min_temp_for_year:.1f} on {custom_date_min_temp}.\n\n" \
                       f"Time : {datetime.now().time()}"

        subject = f"Daily weather post for {datetime.today().date()} [Weather] [Daily]"
        attach = './figures/fig_1.jpeg'
        write_text_to_send(string_blog, file_name='daily_blog_post.txt')

        send_blog(message=read_text_to_email(file_name='daily_blog_post.txt'),
                  subject=subject, file=attach)

        if today.day == 1:  # set as 1 for first day of month
            print('first of month is true, should see monthly blog post')
            # modify so is a monthly report
            # print("this is the first day of the month.")
            last_month = monthrange(today.year, today.month - 1)  # a tuple (# day of week for first day, # days)
           # print(last_month)
          #  print(today.month - 2)
           # date_obj = (datetime.strftime(today, '%B'))
           # print(date_obj)
            # print(month_name[last_month[0]])
            # print(month.)
           # dict_result['time'] = dict_result['time'][(datetime.strftime(dict_result['time'], '%m')) == 6]
          #  print(datetime.strftime(dict_result['time'][1], '%m'))
          #  print(dict_result['time'])
            max_temp_for_month, custom_date_max_temp, min_temp_for_month, custom_date_min_temp = get_last_month_stats(today.month - 1)
            string_blog = f"Today is start of {calendar.month_name[today.month]}.\n\n" \
                          f"Last month the high temperature was {max_temp_for_month:.1f}\u2109 " \
                          f"on {custom_date_max_temp} and " \
                          f"the low was {min_temp_for_month:.1f} on {custom_date_min_temp}.\n\n" \
                          f"Time : {datetime.now().time()}"

            subject = f"Weather summary for {calendar.month_name[today.month - 1]} [Weather] [Monthly]"
            attach = './figures/fig_3.png'
            write_text_to_send(string_blog, file_name='monthly_blog_post.txt')
            send_blog(
                message=read_text_to_email(file_name='monthly_blog_post.txt'),
                subject=subject, file=attach)

        if datetime.today().weekday() == 0:  # if today is Monday 0. sunday 7
            print('new week is true, should see weekly blog post')
            max_temp_for_week, custom_date_max_temp, min_temp_for_week, custom_date_min_temp = get_last_week_stats()
            string_blog = f"Today is start of new week.\n\n" \
                          f"Last week the high temperature was {max_temp_for_week:.1f}\u2109 " \
                          f"on {custom_date_max_temp} and " \
                          f"the low was {min_temp_for_week:.1f} on {custom_date_min_temp}.\n\n" \
                          f"Time : {datetime.now().time()}"

            subject = 'Weekly post [Weather] [Weekly]'
            attach = './figures/fig_2.png'
            write_text_to_send(string_blog, file_name='weekly_blog_post.txt')
            print(string_blog)
            send_blog(message=read_text_to_email(file_name='weekly_blog_post.txt'),
                      subject=subject, file=attach)

    return True


def make_tweet_texts():
    dict_result, hi_dict, wc_result, rain_result = get_data_a()  # get data from SQL

    # make and send freezing tweet
    if dict_result['temp'][-1] < dict_result['temp'][-2] <= 32 < \
            dict_result['temp'][-3]:
        #  if (dict_result['temp'][-1] < 32) and (dict_result['temp'][-2] <= 32) and (
        #          dict_result['temp'][-3] > 32):  # temp falling below set point
        # tweet freeze alert
        string_tweet = f"This is a freeze alert: the temperature is now " \
                       f"{dict_result['temp'][-1]} at {datetime.now()}."
        twitterBot.write_text_to_tweet(string_tweet)
        twitterBot.send_new_tweet(file='tweet_to_send.txt')
        # email / text freeze alert
        string_email = f"This is a freeze email alert: the temperature is now " \
                       f"{dict_result['temp'][-1]}."
        write_text_to_send(string_email)
        send_email(message=read_text_to_email(), subject="FREEZING")

        logger.info(
            f"Is now freezing.\n\ttemp[-1] {dict_result['temp'][-1]} at \n\t time "
            f"{dict_result['time'][-1]}"
            f"\n\t temp[-2] {dict_result['temp'][-2]} at \n\t time {dict_result['time'][-2]}"
            f"\n\t temp[-3] {dict_result['temp'][-3]} at \n\t time {dict_result['time'][-3]}")
    #  make and send above freezing tweet
    if dict_result['temp'][-3] < 32 <= dict_result['temp'][-2] <= \
            dict_result['temp'][-1]:
        #    if (dict_result['temp'][-1] > 32) and (dict_result['temp'][-2] >= 32) and (
        #           dict_result['temp'][-3] < 32):
        # tweet temp above freezing
        string_tweet = f"It is now is above freezing: the temperature is " \
                       f"{dict_result['temp'][-1]} at {datetime.now()}."
        twitterBot.write_text_to_tweet(string_tweet)
        twitterBot.send_new_tweet(file='tweet_to_send.txt')
        # email / text temp above freezing
        string_email = f"This is a temperature email alert: the temperature is now " \
                       f"{dict_result['temp'][-1]}."
        write_text_to_send(string_email)
        send_email(message=read_text_to_email(), subject="Above freezing!")

        logger.info(
            f"Is now above freezing.\n\ttemp[-1] {dict_result['temp'][-1]} at \n\t time "
            f"{dict_result['time'][-1]}"
            f"\n\t temp[-2] {dict_result['temp'][-2]} at \n\t time {dict_result['time'][-2]}"
            f"\n\t temp[-3] {dict_result['temp'][-3]} at \n\t time {dict_result['time'][-3]}")

    #  make and send rain tweet
    if len(dict_result['rain_rate']) > 4:  # RAINING

        if dict_result['rain_rate'][-1] >= dict_result['rain_rate'][-2] > 0.09 >= dict_result['rain_rate'][-3]:
            #       if (dict_result['rain_rate'][-1] > 0.09) and (
            #               dict_result['rain_rate'][-2] > 0.09) and (
            #               dict_result['rain_rate'][-3] <= 0.09):
            send_email(subject="Rain",
                       message=f"raining with rain rate = {dict_result['rain_rate'][-1]}")
            logger.info(
                f"rain rate is raining\n\t rain rate[-1] {dict_result['rain_rate'][-1]} at \n\t"
                f"time {dict_result['time'][-1]}\n\t rain rate[-2] {dict_result['rain_rate'][-2]}"
                f" at \n\t time {dict_result['time'][-2]}\n\t rain rate[-3] "
                f"{dict_result['rain_rate'][-3]} at \n\t time {dict_result['time'][-3]}")

        if dict_result['rain_rate'][-3] >= dict_result['rain_rate'][
            -2] >= 0.09 > \
                dict_result['rain_rate'][-1]:
            #        if (dict_result['rain_rate'][-3] >= 0.09) and (
            #               dict_result['rain_rate'][-2] >= 0.9) and (
            #               dict_result['rain_rate'][-1] < 0.09):
            print("it has stopped raining")
            send_email(subject="Rain",
                       message=f"STOPPED raining with rain rate: {dict_result['rain_rate'][-1]}")
            logger.info(
                f"rain rate has stopped raining\n\train rate[-1] {dict_result['rain_rate'][-1]} at"
                f"\n\t time {dict_result['time'][-1]}\n\t rain rate[-2] "
                f"{dict_result['rain_rate'][-2]} at \n\t time {dict_result['time'][-2]}\n\t"
                f"rain rate[-3] {dict_result['rain_rate'][-3]} at time {dict_result['time'][-3]}")
    #  make and store current temperature tweet
    temperature_tweet_string = f"The temperature is now {dict_result['temp'][-1]}\u2109."
    twitterBot.write_text_to_tweet(string=temperature_tweet_string,
                                   file_name='temperature_tweet.txt')

    if ((dict_result['time'][-1]).day) != date.today().day:
    # if True:
        # print(date.today().day)
        # print((dict_result['time'][-1]).day)
        # make the midnight HI/LOW email
        today = date.today()
        yesterday = today - timedelta(days=1)
        yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
        temp_yesterday = []
        temp_yesterday = dict_result['temp'][
            (dict_result['time']) > yesterday_midnight]
        hi = hi_dict['heat_index'][dates.date2num(hi_dict['time_heat_index']) > (dates.date2num(datetime.now())) - 1]

        max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp = get_year_stats()
        # print(hi)
        # print(len(hi))
        # input('print')
        # hi = [33,]
        string_email = f"The high yesterday was {max(temp_yesterday)} " \
                       f"and the low was {min(temp_yesterday)} \u2109. \n" \
                       f"There was {rain_result['rain_total_yesterday_filtered'][-1]:.1f} " \
                       f"inches of rain yesterday.\n " \
                       f"The high temperature so far this year was {max_temp_for_year:.1f}\u2109 " \
                       f"on {custom_date_max_temp} and the low was {min_temp_for_year:.1f} on {custom_date_min_temp}. \n"

        if len(hi) > 0:
            string_email += f"The max heat index yesterday was {max(hi)}\u2109.\n"

        print(string_email)

        # string_email = 'test mail'
        write_text_to_send(string_email)
        send_email(message=read_text_to_email(), subject="HI LOW")


def make_figures():
    dict_result, hi_result, wc_result, rain_result = get_data_a()  # get data from SQL
    # make and save the figures; then
    make_fig_1(dict_result, hi_result, wc_result, rain_result)
    make_fig_2(dict_result, rain_result, hi_result, wc_result)
    make_fig_3(dict_result, rain_result, hi_result, wc_result)
    # print('made figures')
    return True

def mqtt_app():
    # global DICT_RESULT
    day_1 = datetime.today().date()
    logger.debug(
        "START mqtt_app()\n *******************************************************")
    logger.debug("mqtt_app() call to mqtt_client()")
    mqtt_client()
    # move to mqtt_client
    # logger.debug(f"mqtt_app() call to get_data()\n\tand put return into dict_result")
    # DICT_RESULT = get_data()  # get data from SQL

    # Make Tweets
    # loop_count = 0
    while True:
        logger.debug(
            "mqtt_app()IN WHILE LOOP call to get_data()\n\tand put return into dict_result")
        day_2 = datetime.today().date()
        if day_1 < day_2:  # is a new day
            day_1 = day_2
            make_blog_posts()

        else:  # is not a new day
            pass

        make_figures()
     #   make_tweet_texts()
        # make_email_texts()
        # if new day then send blog post
        # f date.today().day == 2:  # set this
        #    send_blog(message=read_text_to_email(file_name='daily_blog_post.txt'), subject='Monthly report')
        # if new week send new week blog post
        # if new month ...
        #   twitterBot.main()


        pyplot.close(fig='all')
        time.sleep(60)  # cycle main loop every 60 sec
    logger.debug("END mqtt_app()")


if __name__ == "__main__":
    # make_blog_posts()
    try:
        mqtt_app()
    except Exception as exe:
        print(exe)
        logger.error(f"{exe}")
        send_email(subject="ERROR", message=f"{exe}, main unhandled")
        print(traceback.format_exc())
