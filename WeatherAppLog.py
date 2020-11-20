import logging
import Settings
import coloredlogs


def get_a_logger(name):
    logger = logging.getLogger(name)
  #  coloredlogs.install(level='DEBUG')
  #  coloredlogs.DEFAULT_LOG_LEVEL = 50
    coloredlogs.adjust_level(logger=logger, level=10)
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s - Level: %(levelname)s\n  - Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n  - Message: %(message)s \n'

    coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'bold': True, 'color': 'red'},
                                        'debug': {'color': 'green'},
                                        'error': {'color': 'red'},
                                        'info': {'color': 'blue'},
                                        'warning': {'color': 'yellow'}
                                        }

    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'black'},
                                        'hostname': {'color': 'magenta'},
                                        'levelname': {'bold': True, 'color': 'black'},
                                        'name': {'color': 'blue'},
                                        'programname': {'color': 'cyan'},
                                        'username': {'color': 'yellow'}
                                        }


 #   coloredlogs.DEFAULT_LOG_LEVEL = 10

 #   formatter = logging.Formatter('%(asctime)s - Level Name: %(levelname)s\n  - Message: %(message)s \n  - Function: %(funcName)s - Line: %(lineno)s - Module: %(module)s')
 #   chformatter = coloredlogs.ColoredFormatter('%(asctime)s - Level: %(levelname)s\n'
 #                                   '  - Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n'
 #                                   '  - Message: %(message)s \n')
    chformatter = coloredlogs.ColoredFormatter()

 #   fh = logging.FileHandler('MQTTApp.log')
  #  fh.setLevel(logging.DEBUG)  # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
  #  fh.setFormatter(chformatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(chformatter)


#    logger.setLevel(logging.DEBUG)
 #   logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
