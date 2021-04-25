from configparser import ConfigParser
from WeatherAppLog import get_a_logger

logger = get_a_logger(__name__)
"""
refer to: https://www.mysqltutorial.org/python-connecting-mysql-databases/
"""


def read_config(filename='config.ini', section='mysql'):
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
    logger.debug(f"START read_config()\n\t{filename} section: {section}")
    # create a parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            # print("item")
            db[item[0]] = item[1]  # use item[0] as key and item[1] as value in dictionary 'db'
    else:
        raise Exception(f'{section} not found in the {filename} file')
    logger.debug(f" END read_config(): \n\t{filename} section: {section} \n\t{db}")
    return db

