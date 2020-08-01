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
def wind():
    db_connection = mdb.connect(hostname, username, password, dataBaseName)
    cursor = db_connection.cursor()

    query = 'SELECT Date, WS, GS FROM WindSevenDay ORDER BY Date ASC'

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time = []
    ws = []
    gs = []

    for record in result:
        time.append(record[0])
        ws.append(record[1])
        gs.append(record[2])

    wss = signal.savgol_filter(ws, 35, 5)
    gss = signal.savgol_filter(gs, 35, 5)
    fds = [dates.date2num(d) for d in time]
    hfmt = dates.DateFormatter('%m/%d - %H')




    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='green')
    pyplot.xticks(rotation='45')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, wss, marker='o', linestyle='-', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
    ax.plot(fds, gss, marker='o', linestyle='-', color='green', markersize=2.0)
    ax.axis(ymin=0, ymax=8)



    # ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
    ax.set_title("Wind Speed and Gust")
    # pyplot.figtext(0.15, 0.85, f"Temperature now:\n ", horizontalalignment='left', verticalalignment='top')
    # pyplot.figtext(0.75, 0.85, f"Max:  \nMin:  \nAve: ", horizontalalignment='left', verticalalignment='top')

    ax.set_xlabel("Date")
    ax.set_ylabel("MPH")
    ax.grid(which='both', axis='both')
    pyplot.savefig('/var/www/html/WindSevenDayGraph.png')

    # pyplot.show()
    cursor.close()
    db_connection.close()
    fig.clf()
    pyplot.close()
    gc.collect()