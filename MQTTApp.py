# This will communicate with Mosquitto,
# and write into
# main and short datatable

import pymysql as mdb
import paho.mqtt.client as mqtt
import time
import logging
import Settings
import coloredlogs

# import OneDay
# import OneWeek
# import OneMonth
# import OneDayA
# import OneWeekA
# import OneMonthA
# import TestGraph
import gc
from matplotlib import pyplot

import sys
from python_mysql_dbconfig import read_db_config
from WeatherAppLog import get_a_logger

# TODO use argparser to specify debug and desk/pi

Settings.new_data = False
print(f"More new data: {Settings.new_data}")
database_table = Settings.database_table

logger = get_a_logger(__name__)
#coloredlogs.install(level='DEBUG', logger=logger)

"""
connect to Mosquitto MQTT
subscribe to weather channel

connect to SQL
write message data to SQL
"""

def mqtt_app():
 #   global new_data
    mqtt_client()
    while True:
        time.sleep(1)
        if Settings.new_data:
            Settings.new_data = False
            logger.debug(f"call to one_day")
      #      TestGraph.one_day()

   #     OneDayA.one_day()
    #   OneWeekA.one_week()
    #    OneMonthA.one_month()


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
 #   global new_data
  #  logger.info(f"In on_message()")
    full_payload = message.payload.decode()
    index = full_payload.index("MQTT")
    data_string = full_payload[index + 18:-2]
    data_list = data_string.split(',')  # split the string to a list
    logger.debug(f"data list to send to database: \n\t{data_list}")
    write_to_data(data_list)
 #   TestGraph.one_day()  # call to display with  new data
    Settings.new_data = True
    logger.debug(f"new data set to True")


def mqtt_client():
    logger.info(f"Start in mqtt_client()")

    broker_url = Settings.broker_url
    logger.debug(f"MQTT broker url: {broker_url}")
    broker_port = Settings.broker_port
    logger.debug(f"MQTT broker port: {broker_port}")
 #   client = mqtt.Client(client_id='weather2desk', clean_session=False, userdata=None, transport='tcp')

    try:
        client = mqtt.Client(client_id='weather2desk2', clean_session=False, userdata=None, transport='tcp')
        logger.debug("mqtt client created")
    except:
        e = sys.exc_info()[0]
        print(f"client create failed\n\tthe error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

 #   client.loop_start()

 #   client.subscribe('OurWeather', qos=2)
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    try:
        client.connect(broker_url, broker_port)
    except:
        e = sys.exc_info()[0]
        print(f"connect failed\n\tthe error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))
  #  client.subscribe('OurWeather', qos=2)

    try:
        client.subscribe('OurWeather', qos=2)
    except:
        e = sys.exc_info()[0]
        print(f"subscribe failed \n\tthe error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

 #   client.on_subscribe = on_subscribe
  #  client.on_disconnect = on_disconnect
    client.loop_start()


def on_connect(self, userdata, flags, rc):
    logger.info(f"Connected to mosquitto {rc} with client_id {Settings.mqtt_client_id}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
  #  client.subscribe('OurWeather', qos=2)


def on_disconnect(self, userdata, rc):
    logger.info(f'disconnected with rc {rc}')


def on_subscribe(self, userdata, mid, granted_qos):
    logger.info(f"subscribed , with mid:{mid} and granted qos: {granted_qos} to topic OurWeather")


def write_to_data(list_to_write: list) -> object:
    """

    Args:
        list_to_write ():
    """
    logger.info(f"in write_to_data()")
    try:
        db_config = read_db_config()
        logger.debug(f"connection to database with {db_config}")
        db_connection = mdb.connect(**db_config)
        if db_connection.open:
            logger.debug(f"db connect open; success")
        my_cursor = db_connection.cursor()
    except:
       # print("fail to connect to database")
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
        logger.info(f"Successful write to database:\n\t {query}")
        my_cursor.execute(query)
        db_connection.commit()
        db_connection.close()
        if not db_connection.open:
            logger.debug(f"db connection is now closed")
    except:
      #  print("fail to write to database")
        e = sys.exc_info()[0]
    #    print(f"the error is {e}")
    #    print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))


if __name__ == "__main__":

    mqtt_app()
