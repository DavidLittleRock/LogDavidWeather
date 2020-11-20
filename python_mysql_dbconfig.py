from configparser import ConfigParser
import logging
from WeatherAppLog import get_a_logger

logger = get_a_logger(__name__)
"""
refer to: https://www.mysqltutorial.org/python-connecting-mysql-databases/
"""

def read_db_config(filename='config.ini', section='mysql'):
    """
    Read database configuration file and return a dictionary object
    Args:
        filename (): name of the configuration file
        section (): section on the database configuration
    Returns: a dictionary of database parameters
    host =
    database =
    user =
    password =
    """
    # create a parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception(f'{section} not found in the {filename} file')
    logger.debug(f"read_db_config(): \n\t{db}")
    return db
