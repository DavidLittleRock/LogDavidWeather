from WeatherAppLog import get_a_logger
from python_config import read_config
import paho.mqtt.client as mqtt
import sqlfile
import time


logger = get_a_logger(__name__)
logger.setLevel('DEBUG')


def on_log(level, buff):
    """

    Args:
        client ():
        userdata ():
        level ():
        buff ():
    """
    print('mqtt log: ')
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
        "END of on_message() _____________________")


def validate_input(data_list):
    """

    Args:
        data_list ():

    Returns:

    """
    # TODO may add a rain validate here
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
        # send_email(subject="ERROR",
        #            message=f"{v_e}\n\t Temp was: {temperature}")
    try:
        if float(pressure) < 90000 or float(pressure) > 119000:
            valid = False
            raise ValueError("pressure is out of range, ")
    except ValueError as v_e:
        logger.error(f"{v_e}\n\t pressure was: {pressure}")
        # send_email(subject="ERROR",
        #            message=f"{v_e}\n\t pressure was: {pressure}")
    logger.debug("end validate_data()")
    return valid


def mqtt_client():
    """
    make mqtt_client, connect to mqtt, start mqtt loop
    """
    logger.debug(
        "Start in mqtt_client()\n ********")
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
        # send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.on_message = on_message

    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect

    tryagain = 3
    trynum = 0

    while trynum <= tryagain:

        try:
            client.connect(broker_url, broker_port, keepalive=120)
            logger.debug("mqtt client connected")
            trynum = 4
        except OSError as ose:
            trynum += 1
            logger.error(
                f"OS Error, check url or port, {ose}\n\t with url {broker_url} and port {broker_port}")
            # send_email(subject="ERROR",
            #            message=f"OS Error, check url or port, {ose}")
        except Exception as ex:
            trynum += 1
            logger.exception(ex)
            # send_email(subject="ERROR", message=f"The error is: {ex}.")
    try:
        client.subscribe(mqtt_config['topic'], qos=2)
        logger.debug(f"mqtt subscribed to {mqtt_config['topic']}")
    except Exception as ex:
        logger.exception(ex)
        # send_email(subject="ERROR", message=f"The error is: {ex}.")

    client.loop_start()
    logger.debug(
        "end of mqtt_client()\n ____________________________________________________________")


def on_connect(self, userdata, flags, r_c):
    logger.debug("START on_connect()")
    mqtt_config = read_config(section='mqtt')
    # print(f"Connected to mosquitto {r_c} \n\twith client_id: {mqtt_config['mqtt_client_id']}.")
    logger.debug(
        f"Connected to mosquitto {r_c} \n\twith client_id: {mqtt_config['mqtt_client_id']}.")


def on_disconnect(self, userdata, r_c):
    logger.debug(f"MQTT disconnected with rc {r_c}")
    # print(f"MQTT disconnected with rc {r_c}")


def on_subscribe(self, userdata, mid, granted_qos):
    mqtt_config = read_config(section='mqtt')
    logger.debug(
        f"subscribed , with mid:{mid} and granted qos: {granted_qos} \n\tto "
        f"topic: {mqtt_config['topic']}.")


def write_to_data(list_to_write):
    """
    Writes a list of data to a SQL table. The SQL table name
    and other info comes from config.ini, section: sqltable.
    Args:
        list_to_write: type, list. a list of data to write to SQL

    Returns:
        None

    """
    logger.debug("start write_to_data()")
    logger.debug("write_to_data() call to read_config() section sqltable")
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
        # send_email(subject="ERROR", message=f"The error is: {i_e}.")

    logger.debug("end write_to_data()")


if __name__ == '__main__':
    mqtt_client()
    stop = False
    while not stop:
        time.sleep(60)
        quit_it = input('Stop running? Y / n')
        if quit_it.lower() == "y":
            stop = True
