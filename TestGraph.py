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


def make_ax1(ax_dict):
    """

    :param ax_dict:
    :type ax_dict:
    :return:
    :rtype:
    """
    hfmt = dates.DateFormatter('')
    ax1 = ax_dict['fig'].add_subplot(ax_dict['gs'][:5, :4])
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax1.plot(ax_dict['ax1_x1'], ax_dict['ax1_y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['ax1_label1'])
    if ax_dict['ax1_y2'] is not None:
        ax1.plot(ax_dict['ax1_x2'], ax_dict['ax1_y2'], marker='o', linestyle='', color='red', markersize=2.0, label=ax_dict['ax1_label2'])
    if ax_dict['ax1_y3'] is not None:
        ax1.plot(ax_dict['ax1_x1'], ax_dict['ax1_y3'], marker='.', linestyle='-', linewidth=0.5, color='orange', label=ax_dict['ax1_label3'])
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 30 days
#    ax.axis(ymin=10, ymax=110, xmin=math.trunc(dates.date2num(datetime.today()))-0, xmax=math.trunc(dates.date2num(datetime.now()))+1)  # set a 24 hour period midnight to midnight
    ax1.legend()
    ax1.set_title(ax_dict['ax1_title'], fontsize='15')
    ax1.set_xlabel(ax_dict['ax1_xlabel'])
    ax1.set_ylabel(ax_dict['ax1_ylabel'])
    ax1.grid(which='both', axis='both')
    return ax1

def make_ax2(ax_dict):
    hfmt = dates.DateFormatter('')
    ax2 = ax_dict['fig'].add_subplot(ax_dict['gs'][6:8, :4])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(ax_dict['ax1_x1'], ax_dict['ax2_y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=ax_dict['ax2_label'])
    ax2.axis(ymin=0, ymax=5, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax2.legend()
    ax2.set_title(ax_dict['ax2_title'], fontsize='15')
    ax2.set_xlabel(ax_dict['ax2_xlabel'])
    ax2.set_ylabel(ax_dict['ax2_ylabel'])
    ax2.grid(which='both', axis='both')


def make_ax3(ax_dict):
    hfmt = dates.DateFormatter('%m/\n%d')
    ax3 = ax_dict['fig'].add_subplot(ax_dict['gs'][8:, :4])
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(ax_dict['ax1_x1'], ax_dict['ax3_y'], marker='o', linestyle='-', color='green', markersize=1, linewidth=0.5, label=ax_dict['ax3_label'])
    ax3.axis(ymin=29.83, ymax=30.20, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax3.legend()
    ax3.set_title(ax_dict['ax3_title'], fontsize='15')
    ax3.set_xlabel(ax_dict['ax3_xlabel'])
    ax3.set_ylabel(ax_dict['ax3_ylabel'])
    ax3.grid(which='both', axis='both')


def make_ax4(ax_dict):
    hfmt = dates.DateFormatter('')
    ax4 = ax_dict['fig'].add_subplot(ax_dict['gs'][5:6, :4])
    pyplot.xticks([], rotation='45')
    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    ax4.bar(ax_dict['ax4_x'], ax_dict['ax4_y'],  color='blue', label='Rain, inches')
    ax4.axis(ymin=0, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax4.legend()
    ax4.set_title(ax_dict['ax3_title'], fontsize='15')
 #   ax4.set_ylabel("Rain")
    ax4.grid(which='both', axis='both')


def one_month():
    database_name = 'DataLogger'
    database_table = 'OURWEATHERTable'
    database_user_name = 'datalogger'
    database_password = 'Data0233'
    hostname = 'localhost'
    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind FROM OneMonth WHERE MOD(ID, 10) = 0 ORDER BY Date ASC'  # SELECT every 10th
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

    temp_now = temperature[-1]
    max_temp = max(temperature)
    min_temp = min(temperature)
    humid_now = humid[-1]
    baro_now = baro[-1]
    temperature_2 = np.array([temperature])

    fds = [dates.date2num(d) for d in time]  # ax_y

    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
#    heat_index = np.array([heat_index])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]

    xlabel = "Date"
    ylabel = "degree F"

    query = 'SELECT Date, SUM(Rain_Change) FROM OneMonth GROUP BY Day(Date) ORDER BY Date ASC'  # SELECT every 10th
    try:
        cursor.execute(query)
        result_rain = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")

    time = []
    rain = []
    for record in result_rain:
        time.append(record[0])
        rain.append(record[1]/22.5)
    x6 = time
    y6 = rain
    rain_total = sum(y6)

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

    fig = pyplot.figure(num="My Figure", facecolor='green')
    ax_dict = {
        'fig': fig,
        'gs':  fig.add_gridspec(10, 5),

        'ax1_title': None,  # "Temperature",
        'ax1_x1': fds,
        'ax1_y1': temperature,
        'ax1_label1': "Temperature, \u2109",
        'ax1_x2': fds_2,
        'ax1_y2': heat_index_2,
        'ax1_label2': "Heat Index, \u2109",
        'ax1_x3': None,
        'ax1_y3': humid,
        'ax1_label3': "% Humidity",
        'ax1_xlabel': None,
        'ax1_ylabel': None,

        'ax2_title': None,   # "Wind Speed",
        'ax2_x': None,
        'ax2_y': wind,
        'ax2_label': "Wind, MPH",
        'ax2_xlabel': None,
        'ax2_ylabel': None,

        'ax3_title': None,   # "Barometric Pressure",
        'ax3_x': None,
        'ax3_y': baro,
        'ax3_label': "Barometric Pressure, inch Hg",
        'ax3_xlabel': xlabel,
        'ax3_ylabel': None,

        'ax4_x': x6,
        'ax4_y': y6,

    }


    ax1 = make_ax1(ax_dict)
    ax2 = make_ax2(ax_dict)
    ax3 = make_ax3(ax_dict)
    ax4 = make_ax4(ax_dict)

    try:
        pyplot.figtext(0.75, 0.85, f"{time_now}\nTemperature now: {temp_now:.1f} \nHigh: {max_temp:.1f} \nLow: {min_temp:.1f} \nHumidity {humid_now:.0f}%", fontsize=20, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    if temp_now > 80:
        pyplot.figtext(0.75, 0.65, f"The Heat Index is: {heat_index_2[-1]:.1f}", fontsize=15)
    try:
        pyplot.figtext(0.75, 0.49, f"Rain {rain_total:.1f} inches this month", fontsize=15, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    try:
        pyplot.figtext(0.75, 0.40, f"Wind is {result_wind[0][1]*0.6214:.0f} MPH from the {compass[result_wind[0][2]]}", fontsize=15, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    try:
        pyplot.figtext(0.75, 0.25, f"Barometric pressure is {baro_now:.2f} inches Hg", fontsize=15, horizontalalignment='left', verticalalignment='top')
    except IndexError:
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
    pyplot.figtext(0.75, 0.10, f"(Last report time: {result_wind[0][3]})", fontsize=15, horizontalalignment='left', verticalalignment='top')

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
    one_month()
