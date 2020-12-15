import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


"""
30 days of python
"""


def send_email(message):
    host = "smtp.gmail.com"
    port = 587
    username = "DavidWeatherStation@gmail.com"
    password = "Weather123"
    toname = "David.king.lr@gmail.com"  # or can to_list = ["ddd"]
    email_conn = smtplib.SMTP(host, port)
    email_conn.ehlo()
    email_conn.starttls()

    try:
        email_conn.login(username, password)
    except smtplib.SMTPAuthenticationError:
        print("could not log in")

    the_msg = MIMEMultipart(_subtype="alternative")

    the_msg["Subject"] = "ERROR, from David's Weather Station"
    the_msg["From"] = username
    the_msg["To"] = toname
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
    email_conn.sendmail(username, toname, the_msg.as_string())

    email_conn.quit()  # added

#    print(the_msg.as_string())


def main():
    message = "test"
    send_email(message)


if __name__ == '__main__':
    main()
