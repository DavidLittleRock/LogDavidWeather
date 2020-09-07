from configparser import ConfigParser


def read_db_config(filename='config.ini', section='mysql'):
    """
    Read database configuration file and return a dictionary object
    Args:
        filename (): name of the configuration file
        section (): section on the database configuration
    Returns: a dictionary of database parameters
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
    return db
