# This will communicate with Mosquitto,
# and write into
# main and short datatable

import pymysql as mdb
import paho.mqtt.client as mqtt
import time
import logging
import Settings

import OneDay
import OneWeek
import OneMonth
import OneDayA
import OneWeekA
import OneMonthA
import TestGraph
import gc

import sys
from python_mysql_dbconfig import read_db_config
from WeatherAppLog import get_a_logger

# TODO use argparser to specify debug and desk/pi
database_table = Settings.database_table

logger = get_a_logger(__name__)


def mqtt_app():

    mqtt_client()
    while True:
        time.sleep(0.01)
 #       TestGraph.one_day()

        OneDayA.one_day()
        OneWeekA.one_week()
        OneMonthA.one_month()

def on_log(client, userdata, level, buff):
    print(level)
    print(buff)
    return database_password
    raise dd


def on_message(self, userdata, message):
    """
    This function triggered when message received,
    it will parse it into a list of data and
    sends data_list to be writen to DB

    :param self:
    :type self:
    :param userdata: not used
    :type userdata:
    :param message: the message string from Mosquitto MQTT
    :type message: str
    """
    logger.info("In on_message")
    full_payload = message.payload.decode()
    index = full_payload.index("MQTT")
    data_string = full_payload[index + 18:-2]
    data_list = data_string.split(',')  # split the string to a list
    write_to_data(data_list)


def mqtt_client():
    logger.info("in mqtt_client")

    broker_url = Settings.broker_url
    broker_port = Settings.broker_port
    client = mqtt.Client(client_id='myweather2pi', clean_session=False, userdata=None, transport='tcp')

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
        logger.exception(str(e))
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.loop_start()


def on_connect(self, userdata, flags, rc):
    logger.info(f"Connected to mosquitto {rc} with client_id")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('OurWeather', qos=2)


def on_disconnect(self, userdata, rc):
    logger.info(f'disconnected with rc {rc}')


def on_subscribe(self, userdata, mid, granted_qos):
    logger.info(f"subscribed , with mid:{mid} and granted qos: {granted_qos} to topic OurWeather")


def write_to_data(list_to_write: list) -> object:
    """

    Args:
        list_to_write ():
    """
    try:
        db_config = read_db_config()
        # make connection to database
        db_connection = mdb.connect(**db_config)
        my_cursor = db_connection.cursor()
    except:
        print("fail to connect to database")
        e = sys.exc_info()[0]
        logger.exception(str(e))

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
        logger.info(f"Successful write to database:\n {query}")
        my_cursor.execute(query)
        db_connection.commit()
    except:
        print("fail to write to database")
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))


if __name__ == "__main__":

    """
    logger = logging.getLogger('ml')
    logger.setLevel(logging.DEBUG)
    # set up logging to a file
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M', filename='/temp/MQTTApp.log', filemode='w')
    # create a file handler to log to a file
    fh = logging.FileHandler('MQTTApp.log')
    fh.setLevel(logging.DEBUG)
    # create a handler to write to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create a formatter and add to handlers
    formatter = logging.Formatter('%(asctime)s - Level Name: %(levelname)s\n  - Message: %(message)s \n  - Function: %(funcName)s - Line: %(lineno)s - Module: %(module)s')
    chformatter = logging.Formatter('%(asctime)s - Level: %(levelname)s\n'
                                    '  - Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n'
                                    '  - Message: %(message)s \n')

    fh.setFormatter(chformatter)
    ch.setFormatter(chformatter)
    # add the handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)
"""
    mqtt_app()
