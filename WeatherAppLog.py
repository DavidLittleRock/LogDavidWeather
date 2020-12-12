import logging
import Settings
import coloredlogs


def get_a_logger(name):
#    coloredlogs.install(level='DEBUG')

    logger = logging.getLogger(name)
  #  coloredlogs.DEFAULT_LOG_LEVEL = 50
    coloredlogs.adjust_level(logger=logger, level=20)
    """
    Log levels
    Critical    50
    Error       40
    Warning     30
    Info        20 **
    Debug       10
    Notset      0
    """
    coloredlogs.DEFAULT_LOG_FORMAT = ('%(asctime)s - Level: %(levelname)s\n  '
                                      '- Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n  '
                                      '- Message: %(message)s \n  '
                                      '--logger name: %(name)s')

    coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'bold': True, 'color': 'red'},
                                        'debug': {'color': 'green'},
                                        'error': {'color': 'red'},
                                        'info': {'color': 'blue'},
                                        'warning': {'color': 'yellow'}
                                        }

    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'black'},
                                        'hostname': {'color': 'magenta'},
                                        'levelname': {'bold': True},
                                        'name': {'color': 'blue'},
                                        'programname': {'color': 'cyan'},
                                        'username': {'color': 'yellow'},
                                        'module': {'color': 'white'}
                                        }

    chformatter = coloredlogs.ColoredFormatter()

 #   fh = logging.FileHandler('MQTTApp.log')
  #  fh.setLevel(logging.DEBUG)  # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
  #  fh.setFormatter(chformatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(chformatter)

 #   logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
