"""
https://www.freecodecamp.org/news/connect-python-with-sql/
"""

import pymysql as mdb
from pymysql import Error
from configparser import ConfigParser
from WeatherAppLog import get_a_logger

logger = get_a_logger(__name__)
logger.setLevel(20)


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mdb.connect(host=host_name, user=user_name, password=user_password)
        print("sql connect successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("database created")
    except Error as err:
        print(f"Error: '{err}'")


def create_db_connection_x(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mdb.connect(host=host_name, user=user_name, password=user_password, database=db_name)
        print("connected to database")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def create_db_connection():
    connection = None
#    logger = get_a_logger(__name__)
#    log = logger

    try:
        logger.debug("start create_db_connection")
        db_config = read_db_config()
        connection = mdb.connect(**db_config)
        if connection.open:
            logger.debug(f"db connect open; success with:\n\t{db_config}")
    except Error as err:
        logger.debug(f"Error: '{err}'")
    return connection


def close_db_connection(db_connection):
    # close the SQL connection
    log = logger
    db_connection.close()
    if not db_connection.open:
        log.debug(f"db connection closed successfully")
    return


def execute_query(connection, query):
    log = logger
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        log.debug(f"Error: '{err}'")


def read_query(connection, query):
    log = logger
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as err:
        log.debug(f"Error: '{err}'")


def read_db_config(filename='config.ini', section='mysql'):
    """
    Read database configuration file and return a dictionary object
    refer to: https://www.mysqltutorial.org/python-connecting-mysql-databases/

    Args:
        filename (): name of the configuration file
        section (): section on the database configuration
    Returns: a dictionary of database parameters,
    the key must match expected name of the database arguments
    host =
    database =
    user =
    password =
    """
    log = logger

    # create a parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db_kwargs = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_kwargs[item[0]] = item[1]
    else:
        raise Exception(f'{section} not found in the {filename} file')
    log.debug(f"read_db_config() was successful with db_kwargs: \n\t{db_kwargs}")
    return db_kwargs
