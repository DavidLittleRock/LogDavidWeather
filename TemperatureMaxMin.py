import gc
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import dates
# from matplotlib.ticker import MultipleLocator
# from matplotlib.ticker import FormatStrFormatter
# import pylab
# import numpy as np
from numpy import mean
import sys
# from pytz import timezone
# from httplib2 import http
# from datetime import datetime
import pymysql as mdb
# import scipy
# from scipy import signal

database_name = 'DataLogger'
database_table = 'OURWEATHERTable'
database_user_name = 'datalogger'
database_password = 'Data0233'
hostname = 'localhost'
def temp_max_min():
    db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
    cursor = db_connection.cursor()

    query = 'SELECT Date, Max, Min FROM TemperatureMaxMin ORDER BY Date ASC'

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")

    time = []
    maxt = []
    mint = []

    for record in result:
        time.append(record[0])
        maxt.append(record[1])
        mint.append(record[2])


    fds = [dates.date2num(d) for d in time]
    hfmt = dates.DateFormatter('%m/%d')
    low = min(mint)
    high = max(maxt)

    ave = mean(maxt + mint)
    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='green')
    pyplot.xticks(rotation='45')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, maxt, marker='o', linestyle='--', color='red', markersize=2.0)
    # ax.plot(fds, heat_index, c='r')
    ax.plot(fds, mint, marker='o', linestyle='-', color='blue', markersize=2.0)
    ax.axis(ymin=10, ymax=110)



    # ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
    ax.set_title("Temperature Max and Min")
    # pyplot.figtext(0.15, 0.85, f"Temperature now:\n ", horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.85, f"Max: {high:.1f} \nMin: {low:.1f}  \nAve: {ave:.1f} ", fontsize='15', horizontalalignment='left', verticalalignment='top')

    ax.set_xlabel("Date")
    ax.set_ylabel("degree F")
    ax.grid(which='both', axis='both')
    pyplot.savefig('/var/www/html/TemperatureMaxMinGraph.png')
    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()
    pyplot.show(block=False)
    pyplot.pause(15)
    cursor.close()
    db_connection.close()
    pyplot.close()
    gc.collect()
    
if __name__ == '__main__':
    temp_max_min()
