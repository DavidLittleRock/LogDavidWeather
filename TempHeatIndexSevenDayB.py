import gc
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import dates
# from matplotlib.ticker import MultipleLocator
# from matplotlib.ticker import FormatStrFormatter
# import pylab
import numpy as np
from numpy import mean
import sys
# from pytz import timezone
# from httplib2 import http
from datetime import datetime
import pymysql as mdb
# import scipy
# from scipy import signal

database_name = 'DataLogger'
database_table = 'OURWEATHERTable'
database_user_name = 'datalogger'
database_password = 'Data0233'
hostname = 'localhost'

def temp_heat_index():
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
    cursor = db_connection.cursor()

    query = 'SELECT Date, Temp, HI FROM SevenDayTempHeatIndex ORDER BY Date ASC'
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
    time = []
    temperature = []
    heat_index = []
    for record in result:
        time.append(record[0])
        temperature.append(record[1])
        heat_index.append(record[2])
    fds = [dates.date2num(d) for d in time]
    hfmt = dates.DateFormatter('%m/%d')
    x = np.array([fds])
    y = np.array([heat_index])
    x = x[y > 80]  # filter out if heat_index is less than 80
    y = y[y > 80]


    query_max_min = 'SELECT Date, Max, Min FROM TemperatureMaxMin WHERE Date = CURDATE()'
    try:
        cursor.execute(query_max_min)
        result_max_min = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")


    query_wind = 'SELECT id, Current_Wind_Speed, Current_Wind_Direction FROM OURWEATHERTable ORDER BY id LIMIT 1'
    try:
        cursor.execute(query_wind)
        result_wind = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")

    compass = {
        0.0: 'North',
        22.5: 'North',
        45: 'Northeast',
        67.5: 'East',
        90: 'East',
        112.5: 'East',
        135: 'Southeast',
        157.5: 'South',
        180: 'South',
        202.5: 'South',
        225: 'Southwest',
        247.5: 'West',
        270: 'West',
        292.5: 'West',
        315: 'Northwest',
        337.5: 'North',
        360: 'North',
    }

    # fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='green')
    fig = pyplot.figure(num="My Figure", facecolor='green')
    gs = fig.add_gridspec(4, 4)

    # ax = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[1:, :])
    pyplot.xticks(rotation='45')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, temperature, marker='o', linestyle='--', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
    ax.plot(x, y, marker='o', linestyle='', color='orange', markersize=2.0)
    ax.axis(ymin=10, ymax=110)



    ax.set_title("Temperature and Heat Index")
    pyplot.figtext(0.15, 0.85, f"{time_now}\nTemperature now: {temperature[-1]:.1f} \nHigh: {result_max_min[0][1]:.1f} \nLow: {result_max_min[0][2]:.1f} \nWind is {result_wind[0][1]*0.6214:.0f} MPH from the {compass[result_wind[0][2]]}", fontsize=20, horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.85, f"This week: \nMax: {max(temperature):.1f} \nMin: {min(temperature):.1f} \nAve: {mean(temperature):.1f}", fontsize=15, horizontalalignment='left', verticalalignment='top')
    if y[-1] > 80:
        print(y[-1])
        pyplot.figtext(0.75, 0.4, f"The Heat Index is: {y[-1]:.1f}", fontsize=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("degree F")
    ax.grid(which='both', axis='both')
    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph.png')
    mng = pyplot.get_current_fig_manager()
    #    print(mng)
    # ok    mng.resize(*mng.window.maxsize())  # max with window outline
    # no    mng.frame.Maximize(True)
    # no    mng.window.state('zoomed')
    # no   mng.window.showMaximized()
    mng.full_screen_toggle()  # full screen no outline

    pyplot.show(block=False)

    pyplot.pause(60)

    pyplot.close(fig="My Figure")

    cursor.close()
    db_connection.close()
    gc.collect()

if __name__ == '__main__':
    temp_heat_index()
