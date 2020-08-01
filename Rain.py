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
import math

dataBaseName = 'DataLogger'
dataBaseTable = 'OURWEATHERTable'
username = 'datalogger'
password = 'Data0233'
hostname = 'localhost'
def rain():
    db_connection = mdb.connect(hostname, username, password, dataBaseName)
    my_cursor = db_connection.cursor()

    fig, ax = pyplot.subplots(figsize=(10.0, 5.0), facecolor='green', frameon=True, edgecolor='blue')
    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = CURDATE() ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time0 = []
    rain_change0 = []
    rain_sum0 = []

    for record in result:
        time0.append(record[0])
        rain_change0.append(record[1] / 22.5)
        rain_sum0.append(sum(rain_change0))

    today_rain = 0
    if len(rain_sum0)>0:
        today_rain = max(rain_sum0)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time1 = []
    rain_change1 = []
    rain_sum1 = []

    for record in result:
        time1.append(record[0])
        rain_change1.append(record[1] / 22.5)
        rain_sum1.append(sum(rain_change1))

    rain_1 = 0
    if len(rain_sum1)>0:
        rain_1 = max(rain_sum1)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 2 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time2 = []
    rain_change2 = []
    rain_sum2 = []

    for record in result:
        time2.append(record[0])
        rain_change2.append(record[1] / 22.5)
        rain_sum2.append(sum(rain_change2))

    rain_2 = 0
    if len(rain_sum2)>0:
        rain_2 = max(rain_sum2)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 3 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time3 = []
    rain_change3 = []
    rain_sum3 = []

    for record in result:
        time3.append(record[0])
        rain_change3.append(record[1] / 22.5)
        rain_sum3.append(sum(rain_change3))


    rain_3 = 0
    if len(rain_sum3)>0:
        rain_3 = max(rain_sum3)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 4 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time4 = []
    rain_change4 = []
    rain_sum4 = []

    for record in result:
        time4.append(record[0])
        rain_change4.append(record[1] / 22.5)
        rain_sum4.append(sum(rain_change4))

    rain_4 = 0
    if len(rain_sum4)>0:
        rain_4 = max(rain_sum4)


    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 5 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time5 = []
    rain_change5 = []
    rain_sum5 = []

    for record in result:
        time5.append(record[0])
        rain_change5.append(record[1] / 22.5)
        rain_sum5.append(sum(rain_change5))

    rain_5 = 0
    if len(rain_sum5)>0:
        rain_5 = max(rain_sum5)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 6 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time6 = []
    rain_change6 = []
    rain_sum6 = []

    for record in result:
        time6.append(record[0])
        rain_change6.append(record[1] / 22.5)
        rain_sum6.append(sum(rain_change6))

    rain_6 = 0
    if len(rain_sum6)>0:
        rain_6 = max(rain_sum6)

    query = 'SELECT TimeStamp, Rain_Change FROM RainPeriod WHERE DATE(TimeStamp) = DATE_SUB(CURDATE(), INTERVAL 7 DAY) ORDER BY TimeStamp ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
        print(result)
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time7 = []
    rain_change7 = []
    rain_sum7 = []

    for record in result:
        time7.append(record[0])
        rain_change7.append(record[1] / 22.5)
        rain_sum7.append(sum(rain_change7))
    # print(rain_sum7)
    rain_7 = 0
    if len(rain_sum7)>0:
        rain_7 = max(rain_sum7)

    rain_week = today_rain + rain_1 + rain_2 + rain_3 + rain_4 + rain_5 + rain_6 + rain_7

    fds0 = [dates.date2num(d) for d in time0]
    fds1 = [dates.date2num(d) for d in time1]
    fds2 = [dates.date2num(d) for d in time2]
    fds3 = [dates.date2num(d) for d in time3]
    fds4 = [dates.date2num(d) for d in time4]
    fds5 = [dates.date2num(d) for d in time5]
    fds6 = [dates.date2num(d) for d in time6]
    fds7 = [dates.date2num(d) for d in time7]


    hfmt = dates.DateFormatter('%m/%d - %H')


    pyplot.xticks(rotation='45')
    ax.xaxis.set_major_formatter(hfmt)

    if len(fds0) > 0:
        ax.plot(fds0, rain_change0, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds0, rain_sum0, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds1) > 0:
        ax.plot(fds1, rain_change1, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds1, rain_sum1, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds2) > 0:
        ax.plot(fds2, rain_change2, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds2, rain_sum2, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds3) > 0:
        ax.plot(fds3, rain_change3, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds3, rain_sum3, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds4) > 0:
        ax.plot(fds4, rain_change4, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds4, rain_sum4, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds5) > 0:
        ax.plot(fds5, rain_change5, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds5, rain_sum5, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds6) > 0:
        ax.plot(fds6, rain_change6, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds6, rain_sum6, marker='o', linestyle='-', color='orange', markersize=2.0)

    if len(fds7) > 0:
        ax.plot(fds7, rain_change7, marker='o', linestyle='', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
        ax.plot(fds7, rain_sum7, marker='o', linestyle='-', color='orange', markersize=2.0)

    ax.axis(ymin=0, ymax=1, xmin=math.trunc(dates.date2num(datetime.today()))-7, xmax=math.trunc(dates.date2num(datetime.now()))+1)

    # ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
    ax.set_title("Rain")
    pyplot.figtext(0.15, 0.85, f"Rain today : {today_rain:.1f} inches\n ", horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.85, f"Rain this week:  \n{rain_week:.1f}  \nAve: "
                               f"", horizontalalignment='left', verticalalignment='top')

    ax.set_xlabel("Date")
    ax.set_ylabel("Inch")
    ax.grid(which='both', axis='both')
    pyplot.savefig('/var/www/html/RainGraph.png')

    # pyplot.show()
    my_cursor.close()
    db_connection.close()
    fig.clf()
    pyplot.close()
    gc.collect()