# This will communicate with Mosquitto,
# and write into
# main and short datatable

import gc
import time
from datetime import timedelta
from datetime import datetime
from datetime import date
import numpy as np
import paho.mqtt.client as mqtt
from matplotlib import dates
from matplotlib import pyplot
from WeatherAppLog import get_a_logger
from python_config import read_config
import sqlfile
from send_email import send_email
from send_email import write_text_to_email
from send_email import read_text_to_email
import twitterBot
import traceback
from configparser import ConfigParser
# TODO use argparser to specify debug and desk/pi

logger = get_a_logger(__name__)


def on_log(client, userdata, level, buff):
    print(level)
    print(buff)
    pass


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
    logger.debug(f"on_message() started")
    full_payload = message.payload.decode()
    logger.debug(f"message payload: {full_payload}")
    index = full_payload.index("MQTT")
    data_string = full_payload[index + 18:-2]  # trim to just the data string
    data_list = data_string.split(',')  # split the string to a list

    logger.debug(f"on_message() calls validate_input()")
    if validate_input(data_list):
        logger.debug(f"on_message() calls write_to_data()")
        write_to_data(data_list)
    logger.debug(f"data list to send to database: \n\t{data_list}\n\tend of on_message")
    return


def validate_input(data_list):
    logger.debug(f"validate_input started")
    temperature = data_list[0]
    pressure = data_list[2]
    valid = True
    try:
        if float(temperature) < -30.0 or float(temperature) > 50.0:
            valid = False
            raise ValueError("Temperature is out of range, ")
    except ValueError as ve:
        logger.error(f"{ve}\n\t Temp was: {temperature}")
        send_email(subject="ERROR", message=f"{ve}\n\t Temp was: {temperature}")
    try:
        if float(pressure) < 90000 or float(pressure) > 119000:
            valid = False
            raise ValueError("pressure is out of range, ")
    except ValueError as ve:
        logger.error(f"{ve}\n\t pressure was: {pressure}")
        send_email(subject="ERROR", message=f"{ve}\n\t pressure was: {pressure}")
    logger.debug(f"end validate_data()")
    return valid


def mqtt_client():
    logger.debug(f"Start in mqtt_client()")

    mqtt_config = read_config(section='mqtt')
    broker_url = mqtt_config['broker_url']
    logger.debug(f"MQTT broker url: {broker_url}")
    broker_port = int(mqtt_config['broker_port'])
    logger.debug(f"MQTT broker port: {broker_port}")
    try:
        client = mqtt.Client(client_id=mqtt_config['mqtt_client_id'], clean_session=False, userdata=None, transport='tcp')
        logger.debug(f"mqtt client created: id {mqtt_config['mqtt_client_id']}")
    except Exception as ex:
        logger.exception(ex)
        send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    try:
        client.connect(broker_url, broker_port)
    except OSError as ose:
        logger.error(f"OS Error, check url or port, {ose}/n/t with url {broker_url} and port {broker_port}")
        send_email(subject="ERROR", message=f"OS Error, check url or port, {ose}")
    except Exception as ex:
        logger.exception(ex)
        send_email(subject="ERROR", message=f"The error is: {ex}.")
    try:
        client.subscribe(mqtt_config['topic'], qos=2)
    except Exception as ex:
        logger.exception(ex)
        send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.loop_start()
    logger.debug(f"end of mqtt_client()")


def on_connect(self, userdata, flags, rc):
    mqtt_config = read_config(section='mqtt')
    logger.debug(f"Connected to mosquitto {rc} \n\twith client_id: {mqtt_config['mqtt_client_id']}.")


def on_disconnect(self, userdata, rc):
    logger.debug(f"MQTT disconnected with rc {rc}")


def on_subscribe(self, userdata, mid, granted_qos):
    mqtt_config = read_config(section='mqtt')
    logger.debug(f"subscribed , with mid:{mid} and granted qos: {granted_qos} \n\tto topic: {mqtt_config['topic']}.")


def write_to_data(list_to_write):
    """
    Writes a list of data to a SQL table. The SQL table name
    and other info comes from config.ini, sedtion: sqltable.
    Args:
        list_to_write: type, list. a list of data to write to SQL

    Returns:
        None

    """
    logger.debug(f"start write_to_data()")
    logger.debug(f"write_to_data() call to read_config()")
    database_table_t = read_config(section='sqltable')
    database_table = database_table_t['database_table']

    db_connection = sqlfile.create_db_connection()

    device_id = 6
    try:
        query = 'INSERT INTO ' + database_table + (
                ' (timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, Barometric_Pressure, Current_Wind_Speed,'
                'Current_Wind_Gust, Current_Wind_Direction, Wind_Speed_Maximum, Wind_Gust_Maximum, '
                'OurWeather_DateTime, Lightning_Time, Lightning_Distance, Lightning_Count, Rain_Total '
                ') VALUES (CURRENT_TIMESTAMP, %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, "%s", "%s", '
                '%i, %i, %.2f)' % (
                    int(device_id), float(list_to_write[0]), float(list_to_write[1]), float(list_to_write[2]),
                    float(list_to_write[3]), float(list_to_write[4]), float(list_to_write[5]), float(list_to_write[7]),
                    float(list_to_write[8]), list_to_write[9], list_to_write[10], int(list_to_write[11]),
                    int(list_to_write[12]), float(list_to_write[6])))
    except IndexError as ie:
        logger.error(f"failed to build query to write to database,\n\tlength should be 14; {len(list_to_write)}\n\t"
                     f"list to write: {list_to_write}\n\t Error: {ie}")
        send_email(subject="ERROR", message=f"The error is: {ie}.")

    sqlfile.execute_query(db_connection, query)
    sqlfile.close_db_connection(db_connection)
    logger.debug(f"end write_to_data()")

    return


def get_last_id():
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT id FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'
    result = sqlfile.read_query(db_connection, query)
    row_id = result[0][0]
    logger.debug(f"row_id to return: {row_id}; \n\ttype: {type(row_id)}\n\tin get_last_id()")
    sqlfile.close_db_connection(db_connection)  # close the db connection
    return row_id


def get_data():
    """
    Runs a series of SQL queries and combines into a dict
    Returns:
        dict_result: a dict type

    """
    logger.debug("start get_data()")
    db_connection = sqlfile.create_db_connection()
    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP, WC, Gust, Rain_Rate, Rain_Change FROM OneMonth ORDER BY Date ASC'
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
        'time_rain_all': [],
        'time_rain_yesterday_filtered': [],
        'rain_change_yesterday_filtered': [],
        'rain_total_yesterday_filtered': []
    }

    for record in result:  # make a list for each measure
        dict_result['time'].append(record[0])
        dict_result['temp'].append(record[1])
        dict_result['heat_index'].append(record[2])
        dict_result['humid'].append(record[3])
        dict_result['wind_speed'].append(record[4])
        dict_result['wind_d'].append(record[5])
        dict_result['baro_press'].append(record[6])
        dict_result['time_heat_index'].append(record[0])
        dict_result['wind_chill'].append(record[7])
        dict_result['time_wind_chill'].append(record[0])
        dict_result['wind_for_wc'].append(record[4])
        dict_result['gust'].append(record[8])
        dict_result['rain_rate'].append(record[9])
        dict_result['rain_change_all'].append(record[10])  # in mm

    for index in range(len(dict_result['rain_rate'])):  # clean none to 0.0
        if dict_result['rain_rate'][index] is None:
            dict_result['rain_rate'][index] = 0.0

    if len(result_rain_30) > 0:
        for record in result_rain_30:
            dict_result['time_rain_30'].append(record[0])
            try:
                dict_result['rain_30'].append(record[1] / 22.5)
            except TypeError as te:
                logger.error(f"type error {te}\n\t {record}")
                send_email(subject="Error", message=f"type error {te}\nrecord: {record}")
                dict_result['rain_30'].append(0)
            dict_result['rain_30_sum'].append(sum(dict_result['rain_30']))
    else:
        logger.debug(len(result_rain_30))
        dict_result['time_rain_30'].append(0)
        dict_result['rain_30'].append(0)
        dict_result['rain_30_sum'].append(0)

    #    convert each list to a numpy array
    for element in dict_result:
        dict_result[element] = np.array(dict_result[element])

    dict_result['heat_index'] = dict_result['heat_index'][dict_result['temp'] > 80]  # filter heat_index for temp > 80
    dict_result['time_heat_index'] = dict_result['time_heat_index'][dict_result['temp'] > 80]

    dict_result['wind_chill'] = dict_result['wind_chill'][dict_result['temp'] < 50]
    dict_result['time_wind_chill'] = dict_result['time_wind_chill'][dict_result['temp'] < 50]
    dict_result['wind_for_wc'] = dict_result['wind_for_wc'][dict_result['temp'] < 50]
    dict_result['wind_chill'] = dict_result['wind_chill'][dict_result['wind_for_wc'] > 3]
    dict_result['time_wind_chill'] = dict_result['time_wind_chill'][dict_result['wind_for_wc'] > 3]

    #  filter 30 day rain to 7 days
    dict_result['rain_7'] = dict_result['rain_30'][
        dates.date2num(dict_result['time_rain_30']) > dates.date2num(datetime.now()) - 7]

    # yesterday rain
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())
    # yesterday midnight to now
    dict_result['time_rain_yesterday'] = dict_result['time'][(dict_result['time']) > yesterday_midnight]
    dict_result['rain_change_yesterday'] = dict_result['rain_change_all'][(dict_result['time']) > yesterday_midnight]  # in mm
    # yesterday midnight to today midnight
    dict_result['time_rain_yesterday_filtered'] = dict_result['time_rain_yesterday'][(dict_result['time_rain_yesterday']) < today_midnight]
    dict_result['rain_change_yesterday_filtered'] = dict_result['rain_change_yesterday'][(dict_result['time_rain_yesterday']) < today_midnight]  # in mm
    # make cumulative sum
    dict_result['rain_total_yesterday_filtered'] = (np.cumsum(dict_result['rain_change_yesterday_filtered'])/22.5)  # in INCH

    # today midnight to now
    dict_result['time_rain_today'] = dict_result['time'][(dict_result['time']) > today_midnight]
    dict_result['rain_change_today'] = (dict_result['rain_change_all'])[
        (dict_result['time']) > today_midnight]  # in mm
    # make cumulative sum
    dict_result['rain_total_today'] = (np.cumsum(dict_result['rain_change_today'])/22.5)  # in inch
    #   print(dict_result['rain_total_today'])

    # rain 24
    time_24 = datetime.now() - timedelta(days=1)
    dict_result['time_rain_24'] = dict_result['time'][(dict_result['time']) > time_24]
    dict_result['rain_change_24'] = (dict_result['rain_change_all'])[
        (dict_result['time']) > time_24]  # in mm
    # make cumulative sum
    dict_result['rain_total_24'] = (np.cumsum(dict_result['rain_change_24']) / 22.5)  # in inch

    gc.collect()

    dict_clean = clean_dict(dict_result)
    logger.debug(f"END get_data() .....")
    return dict_clean


def clean_dict(dict_result):
    logger.debug(f"clean_dict() started")
    del dict_result['time_rain_yesterday']
    del dict_result['rain_change_yesterday']
    del dict_result['rain_total_yesterday']
    del dict_result['rain_change_today']
    del dict_result['rain_change_24']
    del dict_result['rain_change_all']
    del dict_result['time_rain_all']
    del dict_result['rain_change_yesterday_filtered']

    return dict_result


def make_fig_1(ax_dict):

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
    figure_1 = pyplot.figure(num='one', facecolor='green', figsize=(18.9, 10.4))
    pyplot.suptitle("One Day Graph", fontsize='15', fontweight='bold')
    gs = figure_1.add_gridspec(10, 5)

    hfmt = dates.DateFormatter('')

    day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now())-1]

    try:
        max_temp = max(day_x)
        min_temp = min(day_x)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in ax_temp so will set max_temp and min_temp to 0")
        max_temp = 0
        min_temp = 0
        send_email(subject="ERROR", message=f"The error is: {ve}.")

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline

    # ax1  TEMP
    ax1 = figure_1.add_subplot(gs[:5, :4])
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='', color='black', markersize=2.0,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n(High: {max_temp} Low: {min_temp}) ")


    if len(ax_dict['heat_index']) > 0 and dates.date2num(ax_dict['time_heat_index'][-1]) > (dates.date2num(datetime.now())) - 1:
        ax1.plot(ax_dict['time_heat_index'], ax_dict['heat_index'], marker=6, linestyle='', color='red',
                 label='Heat Index')

    if ax_dict['humid'] is not None:
        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")

    if ax_dict['wind_chill'] is not None and dates.date2num(ax_dict['time_wind_chill'][-1]) > (dates.date2num(datetime.now())) - 1:
        ax1.plot(ax_dict['time_wind_chill'], ax_dict['wind_chill'], marker='v', linestyle='', color='blue',
                 label='Wind chill')

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours

    ax1.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)
    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)

    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(b=True, which='minor', axis='both', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(b=True, which='major', axis='both', color='#666666', linewidth=1.2, linestyle='-')
    ax1.set_facecolor('#edf7f7')

    logger.debug('did make_ax1')

    # ax2  WIND
    # gust period

    gust_period = ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 0.25]
    try:
        max_gust = max(gust_period)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
        send_email(subject="ERROR", message=f"The error is: {ve}. There is no data in the ax_dict['gust'] so is ste to 0 for fig 1.")

    ax2 = figure_1.add_subplot(gs[6:8, :4])

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='-', color='black', markersize=2, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \n from the {compass[ax_dict['wind_d'][-1]]}\n gusting between \n {ax_dict['gust'][-1]:.0f} and {max_gust:.0f} MPH")

    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')

    ax2.set_xlabel('')

    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2)
    ax2.grid(True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')

    # ax3  BP
    ax3 = figure_1.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks([], rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='', color='green', markersize=2.0, linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    hfmt = dates.DateFormatter('%m/%d - %H:%M')
    ax3.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(fontsize=15)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')

    # ax4 RAIN
    ax4 = figure_1.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    ax4.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax4.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_formatter(hfmt)
    # if 1 day
    #  if (ax_dict['title'] == '1 day'):
#    ax4.bar(ax_dict['time_rain_bar'], ax_dict['rain_change_bar'], color='red', width=0.005, label="wwww")
    if len(ax_dict['rain_total_today']) > 0:  # today
        logger.debug(f"Rain today: {ax_dict['rain_total_today']}")
        ax4.plot(ax_dict['time_rain_today'], ax_dict['rain_total_today'], marker='o', linestyle='--', color='green',
                 markersize=1, linewidth=2,
                 label=f"Rain {ax_dict['rain_total_today'][-1]:.1f} inches today")
    else:
        ax_dict['rain_total_today'] = [0.0, 0.0]  # if nothing in rain today then set a 0.0
        logger.debug(f"rain today set to 0 because len was 0")

    if len(ax_dict['rain_total_yesterday_filtered']) > 0:  # yesterday
        logger.debug(f"rain yesterday : {ax_dict['rain_total_yesterday_filtered']}")
        ax4.plot(ax_dict['time_rain_yesterday_filtered'], ax_dict['rain_total_yesterday_filtered'], marker='o', linestyle='--',
                 color='orange', markersize=1, linewidth=2,
                 label=f"Rain {ax_dict['rain_total_yesterday_filtered'][-1]:.1f} inches yesterday")
    else:
        ax_dict['rain_total_yesterday_filtered'] = [0, 0]
    if len(ax_dict['rain_total_24']) > 0:  # 24
        ax4.plot(ax_dict['time_rain_24'], ax_dict['rain_total_24'], marker='o', linestyle='-', color='blue',
                 markersize=1, linewidth=1,
                 label=f"Rain {ax_dict['rain_total_24'][-1]:.1f} inches in 24 hours")
    else:
        ax_dict['rain_total_24'] = [0, 0]
    if len(ax_dict['rain_rate']) > 0:
        ax4.plot(ax_dict['time'], ax_dict['rain_rate'], marker='s', linestyle='', color='blue',
                 markersize=4, linewidth=1,
                 label=f"Rain Rate, inch / hr")

    ax4.axis(ymin=0, ymax=((max(max(ax_dict['rain_total_24']), max(ax_dict['rain_total_today']),
                                max(ax_dict['rain_total_yesterday_filtered']))) + 1) // 1,
             xmin=(dates.date2num(datetime.now())) - 1, xmax=(dates.date2num(datetime.now())))
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax4.grid(True, which='both', axis='both')

    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True, ncol=1, fontsize=15)
    ax4.set_facecolor('#edf7f7')

    pyplot.savefig(fname="./figures/fig_1.jpeg", format='jpeg')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def make_fig_2(ax_dict):

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
    figure_2 = pyplot.figure(num='two', facecolor='green', figsize=(18.9, 10.4))
    pyplot.suptitle("7 Days", fontsize='15', fontweight='bold')
    gs = figure_2.add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')

    day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 7]

    try:
        max_temp = max(day_x)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in day_x so will set max_temp to 0")
        max_temp = 0
        send_email(subject="ERROR", message=f"The error is: {ve}. There is no data in the day_x so is set to 0 for fig 2.")

    try:
        min_temp = min(day_x)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in day_x so will set min_temp to 0")
        min_temp = 0
        send_email(subject="ERROR", message=f"The error is: {ve}. There is no data in the day_x so is set to 0 for fig 2.")
 #   min_temp = min(day_x)

    ax1 = figure_2.add_subplot(gs[:5, :4])

    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='', color='black', markersize=1.5,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n(High: {max_temp} Low: {min_temp})")

#    if ax_dict['hi'] is not None and len(ax_dict['hi']) > 0:  # if there is a Heat Index in the 30 days
#        if ax_dict['time'][-1] == ax_dict['time_hi'][-1]:  # if the last reading has a Heat Index
#            logger.debug(f"temp = {ax_dict['temp'][-1]}")
#            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
#                     label=f"Heat Index {ax_dict['hi'][-1]:.1f}\u2109")
#            print(f"time hi: {ax_dict['time_hi'][-1]} \ntype {type(ax_dict['time_hi'][-1])}")
#            print(f"datetime {datetime.now()}")
#        elif dates.date2num(ax_dict['time_hi'][-1]) > (
#                dates.date2num(datetime.now())) - 1:  # if there is a heat index in 1 day
#            print("ok")
#            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
#                     label=f"Heat Index \u2109")
#        else:  # if no heat index in this day
#            pass
#    else:  # if no heat index in 30 day
#        # do not print Heat Index line
#        pass

    if len(ax_dict['heat_index']) > 0 and dates.date2num(ax_dict['time_heat_index'][-1]) > (dates.date2num(datetime.now())) - 7:
        ax1.plot(ax_dict['time_heat_index'], ax_dict['heat_index'], marker=6, linestyle='', color='red',
                 label='Heat Index')

    if ax_dict['wind_chill'] is not None:
        ax1.plot(ax_dict['time_wind_chill'], ax_dict['wind_chill'], marker='v', linestyle='', color='blue',
                 label='Wind chill', markersize='3.0')
    # block out humid plot
    #    if ax_dict['humid'] is not None:
    #        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
    #                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 7 days
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)

    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')

    logger.debug('did make_ax1')
    ax1.set_facecolor('#edf7f7')

    # ax2  WIND
    ax2 = figure_2.add_subplot(gs[6:8, :4])

    gust_period = ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 0.5]
    try:
        max_gust = max(gust_period)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
        send_email(subject="ERROR", message=f"The error is: {ve}. There is no data in ax_dict['gust'] so will be set to 0. Fig 2.")

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='', color='black', markersize='1.0',
             linewidth=0.5, label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \n from the {compass[ax_dict['wind_d'][-1]]}\n gusting between \n {ax_dict['gust'][-1]:.0f} and {max_gust:.0f} MPH")

    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')
    ax2.set_xlabel('')
    ax2.set_ylabel('MPH')
    ax2.grid(b=True, which='both', axis='both')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')

    # ax3  BP
    ax3 = figure_2.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks([], rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='', color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    hfmt = dates.DateFormatter('%m/%d-%A')
    ax3.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(fontsize=15)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')

    # ax4 RAIN
    ax4 = figure_2.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    #    print(ax_dict['y1'])
    i = 0
    for u in ax_dict['rain_30']:
        if u < 0.01:
            ax_dict['rain_30'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

    #    print(ax_dict['y1'])
    ax4.bar(ax_dict['time_rain_30'], ax_dict['rain_30'], color='blue', width=0.99,
            label=f"Rain {sum(ax_dict['rain_7']):0.1f} inches\n this 7 days", align='edge')
    ax4.axis(ymin=0, ymax=(max(ax_dict['rain_30']) + 1) // 1, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1), shadow=True, ncol=1, fontsize=15)
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax4.grid(b=True, which='both', axis='both')

    ax4.set_facecolor('#edf7f7')

    pyplot.savefig(fname="./figures/fig_2.png", format='png')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def make_fig_3(ax_dict):

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
    figure_3 = pyplot.figure(num='three', facecolor='green', figsize=(18.9, 10.4))
    pyplot.suptitle("30 Days", fontsize='15', fontweight='bold')
    gs = figure_3.add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')

    day_x = ax_dict['temp'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 30]
    max_temp = max(day_x)
    min_temp = min(day_x)

    ax1 = figure_3.add_subplot(gs[:5, :4])

    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='', color='black', markersize=1.0,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109\n(High: {max_temp} Low: {min_temp})")

#    if ax_dict['hi'] is not None and len(ax_dict['hi']) > 0:  # if there is a Heat Index in the 30 days
#        if ax_dict['time'][-1] == ax_dict['time_hi'][-1]:  # if the last reading has a Heat Index
#            logger.debug(f"temp = {ax_dict['temp'][-1]}")
#            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
#                     label=f"Heat Index {ax_dict['hi'][-1]:.1f}\u2109")
#            print(f"time hi: {ax_dict['time_hi'][-1]} \ntype {type(ax_dict['time_hi'][-1])}")
#            print(f"datetime {datetime.now()}")
#        elif dates.date2num(ax_dict['time_hi'][-1]) > (
#                dates.date2num(datetime.now())) - 1:  # if there is a heat index in 1 day
#            print("ok")
#            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
#                     label=f"Heat Index \u2109")
#        else:  # if no heat index in this day
#            pass
#    else:  # if no heat index in 30 day
#        # do not print Heat Index line
#        pass

    if len(ax_dict['heat_index']) > 0 and dates.date2num(ax_dict['time_heat_index'][-1]) > (dates.date2num(datetime.now())) - 30:
        ax1.plot(ax_dict['time_heat_index'], ax_dict['heat_index'], marker=6, linestyle='', color='red',
                 label='Heat Index', markersize='1')

    #    if ax_dict['humid'] is not None:
    #        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
    #                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")

    if ax_dict['wind_chill'] is not None:
        ax1.plot(ax_dict['time_wind_chill'], ax_dict['wind_chill'], marker='v', linestyle='', color='blue',
                 label='Wind chill', markersize='2.0')

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 7 days
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    #    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)

    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')

    logger.debug('did make_ax1')
    ax1.set_facecolor('#edf7f7')

    # ax2  WIND
    ax2 = figure_3.add_subplot(gs[6:8, :4])

    gust_period = ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(datetime.now()) - 1]
    try:
        max_gust = max(gust_period)
    except ValueError as ve:
        logger.error(f"Value Error: {ve}\n\tno data in ax_dict['gust'] so will set max_gust to 0")
        max_gust = 0
        send_email(subject="ERROR", message=f"The error is: {ve}. There is no data in ax_dict['gust'] so is set to 0 in fig 3")
    except Exception as ex:
        logger.error(f"{ex}")
        send_email(subject="ERROR", message=f"{ex}, Fig 3, gust")

    ax2.plot(ax_dict['time'], ax_dict['wind_speed'], marker='o', linestyle='', color='black', markersize=1.5, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind_speed'][-1]:.0f} MPH \n from the {compass[ax_dict['wind_d'][-1]]}\n gusting between \n {ax_dict['gust'][-1]:.0f} and {max_gust:.0f} MPH")

    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    #    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')
    ax2.set_xlabel('')
    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')

    # ax3  BP
    ax3 = figure_3.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks(rotation='25')

    ax3.plot(ax_dict['time'], ax_dict['baro_press'], marker='o', linestyle='', color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['baro_press'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x axis for preceding 24 hours
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    #    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    hfmt = dates.DateFormatter('%m/%d')
    ax3.xaxis.set_major_formatter(hfmt)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')

    # ax4 RAIN
    ax4 = figure_3.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    #    print(ax_dict['y1'])
    i = 0
    for u in ax_dict['rain_30']:
        if u < 0.01:
            ax_dict['rain_30'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

    ax4.bar(ax_dict['time_rain_30'], ax_dict['rain_30'], color='blue', width=0.99,
            label=f"Rain inches,\n {ax_dict['rain_30_sum'][-1]:.1f} total this 30 days", align='edge')
    ax4.axis(ymin=0, ymax=(max(ax_dict['rain_30']) + 1) // 1, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1), shadow=True, ncol=1, fontsize=15)
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(b=True, which='major', color='#666666', linewidth=1.2, linestyle='-', axis='both')
    #   ax4.grid(b=True, which='both', axis='both')

    ax4.set_facecolor('#edf7f7')
    pyplot.savefig(fname="./figures/fig_3.png", format='png')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def is_new_day(day=1):
    return datetime.today().day != day


def make_tweet_texts(dict_result):
    # make and send freezing tweet
    if (dict_result['temp'][-1] < 32) and (dict_result['temp'][-2] <= 32) and (
            dict_result['temp'][-3] > 32):  # temp falling below set point

        string_tweet = f"This is a freeze alert: the temperature is now {dict_result['temp'][-1]} at {datetime.now()}."
        twitterBot.write_text_to_tweet(string_tweet)
        twitterBot.send_new_tweet(file='tweet_to_send.txt')

        string_email = f"This is a freeze email alert: the temperature is now {dict_result['temp'][-1]}."
        write_text_to_email(string_email)
        send_email(message=read_text_to_email(), subject="FREEZING")

        #  send_email(subject="Freeze", message=f"The temperature is below freezing, at {datetime.now()}.")
        logger.info(f"Is now freezing.\n\ttemp[-1] {dict_result['temp'][-1]} at \n\t time {dict_result['time'][-1]}"
                    f"\n\t temp[-2] {dict_result['temp'][-2]} at \n\t time {dict_result['time'][-2]}"
                    f"\n\t temp[-3] {dict_result['temp'][-3]} at \n\t time {dict_result['time'][-3]}")
    #  make and send above freezing tweet

        if (dict_result['temp'][-1] > 32) and (dict_result['temp'][-2] >= 32) and (dict_result['temp'][-3] < 32):  # temp rising above set point
            string_tweet = f"It is now is above freezing: the temperature is {dict_result['temp'][-1]} at {datetime.now()}."
            twitterBot.write_text_to_tweet(string_tweet)
            twitterBot.send_new_tweet(file='tweet_to_send.txt')

            string_email = f"This is a temperature email alert: the temperature is now {dict_result['temp'][-1]}."
            write_text_to_email(string_email)
            send_email(message=read_text_to_email(), subject="Above freezing!")



            #  send_email(subject="Above freezing", message="The temperature is now above freezing.")
            logger.info(
                f"OK  OK  Is now above freezing.\n\ttemp[-1] {dict_result['temp'][-1]} at \n\t time {dict_result['time'][-1]}"
                f"\n\t temp[-2] {dict_result['temp'][-2]} at \n\t time {dict_result['time'][-2]}"
                f"\n\t temp[-3] {dict_result['temp'][-3]} at \n\t time {dict_result['time'][-3]}")

    #  make and send rain tweet
    if len(dict_result['rain_rate']) > 4:  # RAINING
        if (dict_result['rain_rate'][-1] > 0.09) and (dict_result['rain_rate'][-2] > 0.09) and (
                dict_result['rain_rate'][-3] <= 0.09):
            send_email(subject="Rain", message=f"raining with rain rate = {dict_result['rain_rate'][-1]}")
            logger.info(
                f"rain rate is raining\n\t rain rate[-1] {dict_result['rain_rate'][-1]} at \n\t time {dict_result['time'][-1]}"
                f"\n\t rain rate[-2] {dict_result['rain_rate'][-2]} at \n\t time {dict_result['time'][-2]}"
                f"\n\t rain rate[-3] {dict_result['rain_rate'][-3]} at \n\t time {dict_result['time'][-3]}")
        if (dict_result['rain_rate'][-3] >= 0.09) and (dict_result['rain_rate'][-2] >= 0.9) and (
                dict_result['rain_rate'][-1] < 0.09):
            print("it has stopped raining")
            send_email(subject="Rain", message=f"HAS STOPPED raining with rain rate = {dict_result['rain_rate'][-1]}")
            logger.info(
                f"rain rate has stopped raining\n\t rain rate[-1] {dict_result['rain_rate'][-1]} at \n\t time {dict_result['time'][-1]}"
                f"\n\t rain rate[-2] {dict_result['rain_rate'][-2]} at \n\t time {dict_result['time'][-2]}"
                f"\n\t rain rate[-3] {dict_result['rain_rate'][-3]} at \n\t time {dict_result['time'][-3]}")
    #  make and store current temperature tweet
    temperature_tweet_string = f"The temperature is now {dict_result['temp'][-1]}\u2109."
    twitterBot.write_text_to_tweet(string=temperature_tweet_string, file_name='temperature_tweet.txt')

    if is_new_day((dict_result['time'][-1]).day):
        today = date.today()
        yesterday = today - timedelta(days=1)
        yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
        temp_yesterday = []
        temp_yesterday = dict_result['temp'][
            (dict_result['time']) > yesterday_midnight]
        string_email = f"The high yesterday was {max(temp_yesterday)}\u2109 and the low was {min(temp_yesterday)}\u2109." \
                       f" There was {dict_result['rain_total_yesterday_filtered'][-1]:.1f} inches of rain yesterday"
        write_text_to_email(string_email)
        send_email(message=read_text_to_email(), subject="HI LOW")


"""def check_for_new_x(used_id):
    # return False if used_id == get_last_id(), no new data
    last_id = get_last_id()
    if last_id != used_id:
        used_id = last_id
        new_data = True
        dict_result = get_data()
        return used_id, new_data, dict_result
    else:
        new_data = False
        dict_result = get_data()
        return used_id, new_data, dict_result
"""


def mqtt_app():

    mqtt_client()
    logger.debug(f"mqtt_app() call to get_data()")
    dict_result = get_data()  # get data from SQL

    # Make Tweets

    while True:
        # LOOP to :
        time.sleep(1)

        # make and save the figures; then
        make_fig_1(dict_result)
        make_fig_2(dict_result)
        make_fig_3(dict_result)
        make_tweet_texts(dict_result)
        time.sleep(5)
        twitterBot.main()

    #    print(np.average(dict_result['temp'][-3:]))
    #    print(np.average(dict_result['temp'][-6:-4]))
    #    print(np.average(dict_result['temp'][-9:-7]))

        # check if new data, by setting
        used_id = get_last_id()
        new_data = False
        logger.debug(f"Reset new_data back to False")

#        pyplot.figure(num='one')
        while not new_data:
        #    pyplot.figure(num='one')
        #    #         pyplot.show(block=False)
        #    pyplot.pause(75.0)

        #    pyplot.figure(num='two')
            #            pyplot.show(block=False)
        #    pyplot.pause(60.0)

        #    pyplot.figure(num='one')
            #         pyplot.show(block=False)
        #    pyplot.pause(75.0)

        #    pyplot.figure(num='three')
            #            pyplot.show(block=False)
        #    pyplot.pause(60.0)
            #  when there is new data;
            if used_id != get_last_id():
                dict_result = get_data()
                new_data = True
                logger.debug("set new_data to True to trigger break out of new data loop")

        pyplot.close(fig='all')


if __name__ == "__main__":
    try:

        mqtt_app()
    except Exception as e:
        print(e)
        logger.error(f"{e}")
        send_email(subject="ERROR", message=f"{e}, main unhandled")
        print(traceback.format_exc())

    # mqtt_app()
