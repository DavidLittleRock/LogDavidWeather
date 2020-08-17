# This will communicate with Mosquitto,
# and write into
# main and short datatable

import pymysql as mdb
import paho.mqtt.client as mqtt
import time
import TempHeatIndexSevenDay
import TempHeatIndexSevenDayC
import WindSevenDayB
import TemperatureMaxMinB
import BP30B
import BigGraph
import Rain
import WindSevenDay
import GustSevenDayB
import TemperatureMaxMin
import BP30
import OneDay
import gc
# import matplotlib
# matplotlib.use('Agg')
# from matplotlib import pyplot
# from matplotlib import dates
# from matplotlib.ticker import MultipleLocator
# from matplotlib.ticker import FormatStrFormatter
# import pylab
# import numpy as np
# from numpy import mean
import sys
# from pytz import timezone
# from httplib2 import http
# from datetime import datetime
# import scipy
# from scipy import signal

database_name = 'DataLogger'
database_table = 'OURWEATHERTable'
database_user_name = 'datalogger'
database_password = 'Data0233'

hostname = 'localhost'
# user_data_tuple = (hostname, username, password, dataBaseName)

broker_url = '192.168.1.84'
broker_port = 1883
client = mqtt.Client(client_id='myweather2pi', clean_session=False, userdata=None, transport='tcp')

def mqtt_app():

    mqtt_client()
    while True:
        time.sleep(0.1)
        OneDay.one_day()
     #   TempHeatIndexSevenDay.temp_heat_index()
        TempHeatIndexSevenDayC.temp_heat_index()

    #    time.sleep(1)
    #    BigGraph.big_graph()
    #    time.sleep(1)
     #   Rain.rain()
     #   TempHeatIndexSevenDayC.temp_heat_index()

    #    time.sleep(1)
     #   WindSevenDay.wind()
     #   WindSevenDayB.wind()
    #    GustSevenDayB.wind()
      #  TempHeatIndexSevenDayC.temp_heat_index()

    #    time.sleep(1)
     #   TemperatureMaxMin.temp_max_min()
     #   TemperatureMaxMinB.temp_max_min()
      #  TempHeatIndexSevenDayC.temp_heat_index()

    #    time.sleep(1)
     #   BP30.bp()
     #   BP30B.bp()

def on_log(client, userdata, level, buff):
    print(level)
    print(buff)


def on_message(self, userdata, message):
    """This function triggered when message received,
    it will parse it into a list of data and
    sends data_list to be writen to DB
    """
    print("on_message \n")
    full_payload = message.payload.decode()
    index = full_payload.index("MQTT")
    data_string = full_payload[index + 18:-2]
    data_list = data_string.split(',')  # split the string to a list
    print(data_list)
    write_to_data(data_list)


def mqtt_client():
    print("in mqtt_client")

    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect

    try:
        client.connect(broker_url, broker_port)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")


    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    client.loop_start()


def on_connect(self, userdata, flags, rc):
    print(f"Connected to mosquitto {rc} with client_id")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('OurWeather', qos=2)


def on_disconnect(self, userdata, rc):
    print(f'disconnected with rc {rc}')

def on_subscribe(self, userdata, mid, granted_qos):
    print(f"subscribed , with mid:{mid} and granted qos: {granted_qos} to topic OurWeather")


def write_to_data(list_to_write):
    """
    Writes data to the database table
    :param list_to_write: a list if data
    :type list_to_write:
    :return:
    :rtype:
    """

    try:
        db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
        my_cursor = db_connection.cursor()
    except:
        print("fail to connect to database")

    device_id = 6
    try:
        query = 'INSERT INTO ' + database_table + (
            ' (timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, Barometric_Pressure, Current_Wind_Speed, '
            'Current_Wind_Gust, Current_Wind_Direction, Wind_Speed_Maximum, Wind_Gust_Maximum, '
            'OurWeather_DateTime, Lightning_Time, Lightning_Distance, Lightning_Count, Rain_Total, '
            'Rain_Now) VALUES (CURRENT_TIMESTAMP, %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, "%s", "%s", '
            '%i, %i, %.2f, %.3f)' % (
                int(device_id), float(list_to_write[0]), float(list_to_write[1]), float(list_to_write[2]),
                float(list_to_write[3]), float(list_to_write[4]), float(list_to_write[5]), float(list_to_write[7]),
                float(list_to_write[8]), list_to_write[9], list_to_write[10], int(list_to_write[11]),
                int(list_to_write[12]), float(list_to_write[6]), float(list_to_write[13])))
        print(f"Write to database:\n {query}")
        my_cursor.execute(query)
        db_connection.commit()
    except:
        print("fail to write to database")
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")


if __name__ == "__main__":
    mqtt_app()
