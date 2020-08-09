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
import time

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

    timex = []
    temperature = []
    heat_index = []

    for record in result:
        timex.append(record[0])
        temperature.append(record[1])
        heat_index.append(record[2])

    fds = [dates.date2num(d) for d in timex]
    hfmt = dates.DateFormatter('%m/%d')
#     hfmt = dates.DateFormatter('%m/%d - %H')

    x = np.array([fds])
    y = np.array([heat_index])

    x = x[y > 80]  # filter out if heat_index is less than 80
    y = y[y > 80]


    figt, ax = pyplot.subplots(nrows=1,ncols=1,figsize=(17.0, 8.0), facecolor='green', edgecolor='red', linewidth=10)
    pyplot.xticks(rotation='45')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, temperature, marker='o', linestyle='--', color='blue', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
    ax.plot(x, y, marker='o', linestyle='', color='orange', markersize=2.0)
    ax.axis(ymin=10, ymax=110)

 #   print(temperature[-1])
 #   print(max(temperature))

    # ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
    ax.set_title("Temperature and Heat Index")
    pyplot.figtext(0.15, 0.85, f"Temperature: {temperature[-1]:.1f}\n {time_now}", fontsize='xx-large', horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.85, f"Max: {max(temperature):.1f} \nMin: {min(temperature):.1f} \nAve: {mean(temperature):.1f}", horizontalalignment='left', verticalalignment='top')

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
    
    pyplot.pause(6)
#    pyplot.clf()
#    print("clf")
#    pyplot.pause(5)
    pyplot.close(fig=figt)
 #   pyplot.pause(1)

    cursor.close()
    db_connection.close()
    gc.collect()
    time.sleep(1)
    
if __name__ == '__main__':
    temp_heat_index()