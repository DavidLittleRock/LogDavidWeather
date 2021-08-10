import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
#  from configparser import ConfigParser
from WeatherAppLog import get_a_logger
from python_config import read_config
import imghdr
"""
30 days of python
"""
logger = get_a_logger(__name__)


#  def read_email_config(filename='config.ini', section='sendmail'):
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
"""
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
    """


def write_text_to_send(string, file_name='email_to_send.txt'):
    """
    Write a string to a text file
    Args:
        string ():
        file_name ():

    Returns:
        True

    """
    with open(file_name, 'w') as file:
        file.write(string)
    return True


def read_text_to_send(file_name='email_to_send.txt'):
    """
    read text from a file
    Args:
        file_name ():

    Returns:
        text: text string

    """
    with open(file_name, 'r') as file:
        text = file.read()
    return text


def send_email(message="default message", subject="default subject", file='./figures/fig_1.jpeg'):

    #    toname = toname  # or can to_list = ["ddd"]
    em_config = read_config(section='sendmail')
    #  em_config = {'host': '', 'port': '', 'username': '', 'password': '', 'toname': ''}

    tryagain = 3
    trynum = 0
    while trynum <= tryagain:
        try:
            email_conn = smtplib.SMTP(em_config['host'], em_config['port'])
            trynum = 4
        except socket.gaierror:
            print('gai error')
            trynum += 1
            print("try num = ")
            print(trynum)

    email_conn.ehlo()
    email_conn.starttls()

    try:
        email_conn.login(em_config['username'], em_config['password'])
    except smtplib.SMTPAuthenticationError:
        print("could not log in")
    except smtplib.SMTPServerDisconnected:
        print("disconnect")
    the_msg = MIMEMultipart(_subtype="alternative")

    the_msg["Subject"] = subject
    the_msg["From"] = em_config['username']
    the_msg["To"] = em_config['toname']
    the_msg["CC"] = ''
    the_msg["BCC"] = ''
    plain_txt = message
    html_txt = f"""
    <html>
     <head></head>
      <body>
       This is a automatic email message from <b>David's Weather Station</b>. <br>
       {message}
       <br>
       Thank You.
      </body>
    </html>
    """
    # file = './figures/fig_1.jpeg'
    with open(file, 'rb') as fp:
        img_data = MIMEImage(fp.read(), filename="weather graph")
    the_msg.attach(img_data)

    part_1 = MIMEText(plain_txt, "plain")
    part_2 = MIMEText(html_txt, "html")

    the_msg.attach(part_1)
    the_msg.attach(part_2)
    email_conn.sendmail(em_config['username'], em_config['toname'], the_msg.as_string())

    email_conn.quit()  # added

    return True


def send_blog(message="default message", subject="default subject", file='./figures/fig_1.jpeg'):

    #    toname = toname  # or can to_list = ["ddd"]
    em_config = read_config(section='sendblog')
    #  em_config = {'host': '', 'port': '', 'username': '', 'password': '', 'toname': ''}

    tryagain = 3
    trynum = 0
    while trynum <= tryagain:
        try:
            email_conn = smtplib.SMTP(em_config['host'], em_config['port'])
            trynum = 4
        except socket.gaierror:
            print('gai error')
            trynum += 1
            print("try num = ")
            print(trynum)

    email_conn.ehlo()
    email_conn.starttls()

    try:
        email_conn.login(em_config['username'], em_config['password'])
    except smtplib.SMTPAuthenticationError:
        print("could not log in")
    except smtplib.SMTPServerDisconnected:
        print("disconnect")
    the_msg = MIMEMultipart(_subtype="alternative")

    the_msg["Subject"] = subject
    the_msg["From"] = em_config['username']
    the_msg["To"] = em_config['toname']
    the_msg["CC"] = ''
    the_msg["BCC"] = ''
    plain_txt = message
    html_txt = f"""
    <html>
     <head></head>
      <body>
       This is a automatic post from <b>David's Weather Station</b>. <br><br>
       {message}
       <br>
     </body>
    </html>
    """
    with open(file, 'rb') as fp:
        img_data = MIMEImage(fp.read())
    the_msg.attach(img_data)

    part_1 = MIMEText(plain_txt, "plain")
    part_2 = MIMEText(html_txt, "html")

    the_msg.attach(part_1)
    the_msg.attach(part_2)
    email_conn.sendmail(em_config['username'], em_config['toname'], the_msg.as_string())

    email_conn.quit()  # added

    return True


def main():
    message = "test"
    send_email(subject="error", message=message)


if __name__ == '__main__':
    main()
