import logging

def get_a_logger(name):
    formatter = logging.Formatter('%(asctime)s - Level Name: %(levelname)s\n  - Message: %(message)s \n  - Function: %(funcName)s - Line: %(lineno)s - Module: %(module)s')
    chformatter = logging.Formatter('%(asctime)s - Level: %(levelname)s\n'
                                    '  - Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n'
                                    '  - Message: %(message)s \n')

    fh = logging.FileHandler('MQTTApp.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(chformatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(chformatter)

    logger = logging.getLogger('ml')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger