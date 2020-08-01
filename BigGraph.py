import gc
import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import dates
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FormatStrFormatter
import pylab
import numpy as np
from numpy import mean
import sys
from pytz import timezone
from httplib2 import http
from datetime import datetime
import pymysql as mdb
import scipy
from scipy import signal

dataBaseName = 'DataLogger'
dataBaseTable = 'OURWEATHERTable'
username = 'datalogger'
password = 'Data0233'
hostname = 'localhost'
def big_graph():
    db_connection = mdb.connect(hostname, username, password, dataBaseName)
    cursor = db_connection.cursor()

    query = 'SELECT TimeStamp, Outdoor_Temperature, Outdoor_Humidity, Barometric_Pressure, ' \
            'Current_Wind_Speed FROM OURWEATHERTable WHERE DATE(TimeStamp) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) ORDER BY TimeStamp ASC '

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time = []
    temperature = []
    humidity = []
    baro = []
    wind = []

    for record in result:
        time.append(record[0])
        temperature.append(record[1]*9/5+32)
        humidity.append(record[2])
        baro.append(record[3]/3386.4)
        wind.append(record[4])



    fds = [dates.date2num(d) for d in time]
    hfmt = dates.DateFormatter('%m/%d - %H')


    fig, (ax, ax2, ax3) = pyplot.subplots(3, figsize=(17.0, 8.0), facecolor='green')
    pyplot.xticks(rotation='45')
    ax.set_frame_on(False)
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, temperature, marker='o', linestyle='--', color='blue', markersize=2.0)
    ax.plot(fds, humidity, marker='o', linestyle='-', color='red', markersize=2.0)
    ax2.plot(fds, baro, marker='o', linestyle='-', color='green', markersize=2.0)
    ax3.plot(fds, wind, marker='o', linestyle='-', color='orange', markersize=2.0)

    ax.axis(ymin=0, ymax=110)

    print(temperature[-1])
    print(max(temperature))

    # ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
    ax.set_title("Temperature and Heat Index")
    pyplot.figtext(0.15, 0.85, f"Temperature now:\n {temperature[-1]:.1f}", horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.85, f"Max: {max(temperature):.1f} \nMin: {min(temperature):.1f} \nAve: {mean(temperature):.1f}", horizontalalignment='left', verticalalignment='top')

    ax.set_xlabel("Date")
    ax.set_ylabel("degree F")
    ax.grid(which='both', axis='both')
    pyplot.savefig('/var/www/html/BigGraph.png')

    # pyplot.show()
    cursor.close()
    db_connection.close()
    fig.clf()
    pyplot.close()
    gc.collect()