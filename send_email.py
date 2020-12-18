import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser
from WeatherAppLog import get_a_logger
from python_config import read_config
"""
30 days of python
"""
logger = get_a_logger(__name__)


def read_email_config(filename='config.ini', section='sendmail'):
    """
    Read database configuration file and return a dictionary object
    refer to: https://www.mysqltutorial.org/python-connecting-mysql-databases/

    Args:
        filename (): name of the configuration file
        section (): section on the database configuration
    Returns: a dictionary of email parameters,
    the key must match expected name of the database arguments
    =
    """
    # create a parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to sendmail
    db = {}
    if parser.has_section(section):
        items = parser.items(section)  # parser makes a list or tuples
        for item in items:  # for each tuple in the list
            db[item[0]] = item[1]  # make a dict with key = first thing in tuple and value is second
    else:
        raise Exception(f'{section} not found in the {filename} file')
    logger.debug(f"read_email_config(): \n\t{db}")
    #  db = {'host': '', 'port': '', 'username': '', 'password': '', 'toname': ''}

    return db


def send_email(message):

    #    toname = toname  # or can to_list = ["ddd"]
    em_config = read_config(section='sendmail')
    #  em_config = {'host': '', 'port': '', 'username': '', 'password': '', 'toname': ''}

    email_conn = smtplib.SMTP(em_config['host'], em_config['port'])
    email_conn.ehlo()
    email_conn.starttls()

    try:
        email_conn.login(em_config['username'], em_config['password'])
    except smtplib.SMTPAuthenticationError:
        print("could not log in")
    except smtplib.SMTPServerDisconnected:
        print("disconnect")
    the_msg = MIMEMultipart(_subtype="alternative")

    the_msg["Subject"] = "ERROR, from David's Weather Station"
    the_msg["From"] = em_config['username']
    the_msg["To"] = em_config['toname']
    the_msg["CC"] = ''
    the_msg["BCC"] = ''
    plain_txt = message
    html_txt = f"""
    <html>
     <head></head>
      <body>
       This is a automatic message from David's Weather Station. <br>
       {message}
       <br>
       Thank You.
      </body>
    </html>
    """
    part_1 = MIMEText(plain_txt, "plain")
    part_2 = MIMEText(html_txt, "html")

    the_msg.attach(part_1)
    the_msg.attach(part_2)
    email_conn.sendmail(em_config['username'], em_config['toname'], the_msg.as_string())

    email_conn.quit()  # added

#    print(the_msg.as_string())


def main():
    message = "test"
#   send_email(message, re)


if __name__ == '__main__':
    main()
