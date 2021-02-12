import logging
import coloredlogs
import logging.handlers
import smtplib


def get_a_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    """
    Log levels
    Critical    50
    Error       40
    Warning     30
    Info        20 **
    Debug       10
    Notset      0
    """
    """
    coloredlogs.DEFAULT_LOG_FORMAT = ('%(asctime)s - Level: %(levelname)s\n  '
                                      '- Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n  '
                                      '- Message: %(message)s \n  '
                                      '--logger name: %(name)s')
                                      """

    coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'bold': True, 'color': 'red'},
                                        'debug': {'color': 'green'},
                                        'error': {'color': 'red'},
                                        'info': {'color': 'blue'},
                                        'warning': {'color': 'yellow'}
                                        }

    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'blue'},
                                        'hostname': {'color': 'magenta'},
                                        'levelname': {'bold': True},
                                        'name': {'color': 'blue'},
                                        'programname': {'color': 'cyan'},
                                        'username': {'color': 'yellow'},
                                        'module': {'color': 'white'}
                                        }

    chcformatter = coloredlogs.ColoredFormatter(fmt=('%(asctime)s - Level: %(levelname)s\n  '
                                      '- Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n  '
                                      '- Message: %(message)s \n  '
                                      '--logger name: %(name)s'))

    chformatter = logging.Formatter('%(asctime)s - Level: %(levelname)s\n  '
                                                    '- Module: %(module)s  - Function: %(funcName)s - Line #: %(lineno)s\n  '
                                                    '- Message: %(message)s \n  '
                                                    '--logger name: %(name)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(chcformatter)
    logger.addHandler(ch)

    trfh = logging.handlers.TimedRotatingFileHandler(filename='./LOGS/Weather.log',  when='H', interval=1, backupCount=6)
    trfh.setLevel(logging.INFO)
    trfh.setFormatter(chformatter)
    logger.addHandler(trfh)

    securex = ()
    smtph = logging.handlers.SMTPHandler(('smtp.gmail.com', 587), 'DavidWeatherStation@gmail.com', ['david.king.lr@gmail.com'], 'error', credentials=('DavidWeatherStation@gmail.com', 'Weather123'), secure=None)
    smtph.setLevel(logging.ERROR)
    smtph.setFormatter(chformatter)
#    logger.addHandler(smtph)

    return logger
