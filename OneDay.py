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
import math


# db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
# cursor = db_connection.cursor()


def make_ax(ax_dict):
    gs = ax_dict['fig'].add_gridspec(4, 4)
    hfmt = dates.DateFormatter('')
    ax = ax_dict['fig'].add_subplot(gs[:2, :3])
    ax.xaxis.set_major_locator(dates.HourLocator(interval=4))
    ax.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax.plot(ax_dict['ax_x1'], ax_dict['ax_y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['ax_label1'])
    if ax_dict['ax_y2'] is not None:
        ax.plot(ax_dict['ax_x2'], ax_dict['ax_y2'], marker='o', linestyle='', color='red', markersize=2.0, label=ax_dict['ax_label2'])
    if ax_dict['ax_y3'] is not None:
        ax.plot(ax_dict['ax_x1'], ax_dict['ax_y3'], marker='.', linestyle='', color='orange', label=ax_dict['ax_label3'])
    ax.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
#    ax.axis(ymin=10, ymax=110, xmin=math.trunc(dates.date2num(datetime.today()))-0, xmax=math.trunc(dates.date2num(datetime.now()))+1)  # set a 24 hour period midnight to midnight
    ax.legend()
    ax.set_title(ax_dict['ax_title'], fontsize='15')
    ax.set_xlabel(ax_dict['ax_xlabel'])
    ax.set_ylabel(ax_dict['ax_ylabel'])
    ax.grid(which='both', axis='both')


def make_ax2(ax_dict):
    gs = ax_dict['fig'].add_gridspec(4, 4)
    hfmt = dates.DateFormatter('')
    ax2 = ax_dict['fig'].add_subplot(gs[2:3, :3])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=4))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(ax_dict['ax_x1'], ax_dict['ax2_y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=ax_dict['ax2_label'])
    ax2.axis(ymin=0, ymax=5, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax2.legend()
    ax2.set_title(ax_dict['ax2_title'], fontsize='15')
    ax2.set_xlabel(ax_dict['ax2_xlabel'])
    ax2.set_ylabel(ax_dict['ax2_ylabel'])
    ax2.grid(which='both', axis='both')



def make_ax3(ax_dict):
    gs = ax_dict['fig'].add_gridspec(4, 4)
    hfmt = dates.DateFormatter('%m/%d \n %H:%M')
    ax3 = ax_dict['fig'].add_subplot(gs[3:, :3])
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.HourLocator(interval=4))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(ax_dict['ax_x1'], ax_dict['ax3_y'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1, label=ax_dict['ax3_label'])
    ax3.axis(ymin=29.83, ymax=30.20, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax3.legend()
    ax3.set_title(ax_dict['ax3_title'], fontsize='15')
    ax3.set_xlabel(ax_dict['ax3_xlabel'])
    ax3.set_ylabel(ax_dict['ax3_ylabel'])
    ax3.grid(which='both', axis='both')



def one_day():
    database_name = 'DataLogger'
    database_table = 'OURWEATHERTable'
    database_user_name = 'datalogger'
    database_password = 'Data0233'
    hostname = 'localhost'
    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind FROM OneDay ORDER BY Date ASC'
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")

    time = []
    temperature = []
    heat_index = []
    humid = []
    baro = []
    wind = []
    for record in result:
        time.append(record[0])
        temperature.append(record[1])  # ax_x1
        heat_index.append(record[2])
        humid.append(record[3])
        baro.append(record[4])
        wind.append(record[5])
    fds = [dates.date2num(d) for d in time]  # ax_y
    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
    temperature_2 = np.array([temperature])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]
#    label1 = "Temperature, \u2109"  # \u2109 is degree F
#    label2 = "Heat Index, \u2109"
#    label3 = "Humidity, %"
#    title = "Temperature past 24 hours"
    xlabel = "Date"
    ylabel = "degree F"
#    ylabel3 = "MPH"
#    label4 = "Wind, MPH"
#    label5 = "Barometric Pressure, inch Hg"


#    query_max_min = 'SELECT Date, Max, Min FROM TemperatureMaxMin WHERE Date = CURDATE()'
 #   try:
 #       cursor.execute(query_max_min)
  #      result_max_min = cursor.fetchall()
 #   except:
 #       e = sys.exc_info()[0]
 #       print(f"the error is {e}")
   # print(result_max_min)   # if returns empty need way to still print

    query_wind = 'SELECT id, Current_Wind_Speed, Current_Wind_Direction, OurWeather_DateTime FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'
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
 #   gs = fig.add_gridspec(1, 4)
  #  gs = ax_dict['fig'].add_gridspec(4, 4)

    ax_dict = {
        'fig': fig,

        'ax_title': "Temperature",
        'ax_x1': fds,
        'ax_y1': temperature,
        'ax_label1': "Temperature, \u2109",
        'ax_x2': fds_2,
        'ax_y2': heat_index_2,
        'ax_label2': "Heat Index, \u2109",
        'ax_x3': None,
        'ax_y3': humid,
        'ax_label3': "% Humidity",
        'ax_xlabel': None,
        'ax_ylabel': None,

        'ax2_title': "Wind Speed",
        'ax2_x': None,
        'ax2_y': wind,
        'ax2_label': "Wind, MPH",
        'ax2_xlabel': None,
        'ax2_ylabel': None,

        'ax3_title': "Barometric Pressure",
        'ax3_x': None,
        'ax3_y': baro,
        'ax3_label': "Barometric Pressure, inch Hg",
        'ax3_xlabel': xlabel,
        'ax3_ylabel': None,


    }


    ax = make_ax(ax_dict)
    ax2 = make_ax2(ax_dict)
    ax3 = make_ax3(ax_dict)


    try:
        pyplot.figtext(0.73, 0.85, f"{time_now}\nTemperature now: {temperature[-1]:.1f} \nHigh: {max(temperature):.1f} \nLow: {min(temperature):.1f} \nHumidity {humid[-1]:.0f}%", fontsize=20, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    if temperature[-1] > 80:
     #   print(y[-1])
        pyplot.figtext(0.73, 0.65, f"The Heat Index is: {heat_index_2[-1]:.1f}", fontsize=15)
    try:
        pyplot.figtext(0.73, 0.45, f"Wind is {result_wind[0][1]*0.6214:.0f} MPH from the {compass[result_wind[0][2]]}", fontsize=15, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    try:
        pyplot.figtext(0.73, 0.25, f"Barometric pressure is {baro[-1]:.2f} inches Hg", fontsize=15, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    pyplot.figtext(0.73, 0.10, f"(Last report time: {result_wind[0][3]})", fontsize=15, horizontalalignment='left', verticalalignment='top')

    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph.png')
    mng = pyplot.get_current_fig_manager()

    mng.full_screen_toggle()  # full screen no outline

    pyplot.show(block=False)
    pyplot.pause(120)
    pyplot.close(fig="My Figure")



    cursor.close()
    db_connection.close()
    gc.collect()

if __name__ == '__main__':
    one_day()
