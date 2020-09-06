import gc
from typing import Any
from typing import Dict
from matplotlib import pyplot
from matplotlib import dates
import numpy as np
from numpy import mean
import sys
from datetime import datetime
import pymysql as mdb
import math
import Settings
import logging

ax_dict: Dict[Any, Any] = {}
logger = logging.getLogger('ml')


def make_ax1(ax_dict):
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax = ax_dict['fig'].add_subplot(gs[:5, :4])
    ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax.plot(ax_dict['ax1_x1'], ax_dict['ax1_y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['ax1_legend1'])
    if ax_dict['ax1_y2'] is not None:
#        print(ax_dict['ax1_y2'])
        if ax_dict['ax1_y1'][-1] >= 80:
            ax.plot(ax_dict['ax1_x2'], ax_dict['ax1_y2'], marker='o', linestyle='', color='red', markersize=2.0, label=ax_dict['ax1_legend2'])
        else:
            ax.plot(ax_dict['ax1_x2'], ax_dict['ax1_y2'], marker='o', linestyle='', color='red', markersize=2.0, label=ax_dict['ax1_legend2a'])
    if ax_dict['ax1_y3'] is not None:
        ax.plot(ax_dict['ax1_x1'], ax_dict['ax1_y3'], marker='.', linestyle='', color='orange', label=ax_dict['ax1_legend3'])
    ax.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
#    ax.axis(ymin=10, ymax=110, xmin=math.trunc(dates.date2num(datetime.today()))-0, xmax=math.trunc(dates.date2num(datetime.now()))+1)  # set a 24 hour period midnight to midnight
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax.set_title(ax_dict['ax1_title'], fontsize='15')
    ax.set_xlabel(ax_dict['ax1_xlabel'])
    ax.set_ylabel(ax_dict['ax1_ylabel'])
    ax.grid(which='both', axis='both')
    ax.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax.grid(which='major', color='#666666', linewidth=1.2)
    logger.debug('did make_ax1')
def make_ax2(ax_dict):
    """
    wind

    Args:
        ax_dict ():
    """
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax2 = ax_dict['fig'].add_subplot(gs[6:8, :4])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(ax_dict['ax1_x1'], ax_dict['ax2_y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=ax_dict['ax2_legend'])
    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title(ax_dict['ax2_title'], fontsize='15')
    ax2.set_xlabel(ax_dict['ax2_xlabel'])
    ax2.set_ylabel(ax_dict['ax2_ylabel'])
    ax2.grid(which='both', axis='both')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2)

def make_ax3(ax_dict):
    """
    barometric pressure
    Args:
        ax_dict ():
    """
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('%m/%d \n %H:%M')
    ax3 = ax_dict['fig'].add_subplot(gs[8:, :4])
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(ax_dict['ax1_x1'], ax_dict['ax3_y'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1, label=ax_dict['ax3_legend'])
    ax3.axis(ymin=29.50, ymax=30.35, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title(ax_dict['ax3_title'], fontsize='15')
    ax3.set_xlabel(ax_dict['ax3_xlabel'])
    ax3.set_ylabel(ax_dict['ax3_ylabel'])
    ax3.grid(which='both', axis='both')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2)


def make_ax4(ax_dict):
    """
RAIN
    Args:
        ax_dict ():
    """
    gs = ax_dict['fig'].add_gridspec(10, 5)

    hfmt = dates.DateFormatter('')
    ax4 = ax_dict['fig'].add_subplot(gs[5:6, :4])

    pyplot.xticks([], rotation='45')
    ax4.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax4.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    ax4.bar(ax_dict['ax4_x'], ax_dict['ax4_y'],  color='blue', width=0.005, label='Rain, inches')
    if len(ax_dict['ax4_y3']) > 0:
        ax4.plot(ax_dict['ax4_x3'], ax_dict['ax4_y3'], marker='o', linestyle='--', color='green', markersize=1, linewidth=2, label= f"Rain today, {ax_dict['ax4_y3'][-1]:.1f} inch")
    if len(ax_dict['ax4_y4']) > 0:
        ax4.plot(ax_dict['ax4_x4'], ax_dict['ax4_y4'], marker='o', linestyle='--', color='orange', markersize=1, linewidth=2, label= f"Rain yesterday, {ax_dict['ax4_y4'][-1]:.1f} inch")
    if len(ax_dict['ax4_y5']) > 0:
        ax4.plot(ax_dict['ax4_x5'], ax_dict['ax4_y5'], marker='o', linestyle='--', color='blue', markersize=1, linewidth=2, label= f"Rain 24 hours {ax_dict['ax4_y5'][-1]:.1f} inch")
    ax4.axis(ymin=0, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax4.set_title(ax_dict['ax3_title'], fontsize='15')
 #   ax4.set_ylabel("Rain")
    ax4.grid(which='both', axis='both')
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2)
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True, ncol=1, fontsize=15)


def one_day():
    database_name = Settings.database_name
    database_table = Settings.database_table
    database_user_name = Settings.database_user_name
    database_password = Settings.database_password
    hostname = Settings.hostname
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    db_connection = mdb.connect(hostname, database_user_name, database_password, database_name)
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind, Wind_Direction, Rain_Change, Gust FROM OneDay ORDER BY Date ASC'  # this rain will be 48 Hours, not usefull
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    time = []
    temperature = []
    heat_index = []
    humid = []
    baro = []
    wind = []
    wind_direct = []
    rain_change = []
    rain_total = []
    gust = []
    for record in result:
        time.append(record[0])
        temperature.append(record[1])  # ax_x1
        heat_index.append(record[2])
        humid.append(record[3])
        baro.append(record[4])
        wind.append(record[5])
        wind_direct.append(record[6])
        rain_change.append(record[7]/22.5)
        rain_total.append(sum(rain_change))
        gust.append(record[8])
    fds = [dates.date2num(d) for d in time]  # ax_y
    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
    temperature_2 = np.array([temperature])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]
    logger.debug(f"heat_index_2: {heat_index_2}")
#    label1 = "Temperature, \u2109"  # \u2109 is degree F
#    label2 = "Heat Index, \u2109"
#    label3 = "Humidity, %"
#    title = "Temperature past 24 hours"
    xlabel = "Date"
    ylabel = "degree F"
#    ylabel3 = "MPH"
#    label4 = "Wind, MPH"
#    label5 = "Barometric Pressure, inch Hg"

  #  query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(DATE_SUB(CURDATE(), INTERVAL 1 DAY)) ORDER BY Date ASC'
    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(DATE_SUB(CURDATE(), INTERVAL 1 DAY)) ORDER BY Date ASC'  # Yesterday 00:00 to 00:00

    try:
        cursor.execute(query)
        result_rain_yesterday = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    time_rain_yesterday = []

    rain_change_yesterday = []
    rain_total_yesterday = []
    for record in result_rain_yesterday:
        time_rain_yesterday.append(record[0])

        rain_change_yesterday.append(record[1] / 22.5)
        rain_total_yesterday.append(sum(rain_change_yesterday))
    fds_rain_yesterday = [dates.date2num(d) for d in time_rain_yesterday]  # ax_y
 #   print("rain yesterday")
 #   print(rain_total_yesterday)

    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(CURDATE()) ORDER BY Date ASC'  # Today start 00:00 to now

    try:
        cursor.execute(query)
        result_rain_today = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    time_rain_today = []

    rain_change_today = []
    rain_total_today = []
    for record in result_rain_today:
        time_rain_today.append(record[0])

        rain_change_today.append(record[1] / 22.5)
        rain_total_today.append(sum(rain_change_today))
    fds_rain_today = [dates.date2num(d) for d in time_rain_today]  # ax_y
 #   print("rain today >>>")
 #   print(rain_total_today)

    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Date >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR) ORDER BY Date ASC'  # 24 hr rain

    try:
        cursor.execute(query)
        result_rain_24 = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    time_rain_24 = []

    rain_change_24 = []
    rain_total_24 = []
    for record in result_rain_24:
        time_rain_24.append(record[0])
        rain_change_24.append(record[1] / 22.5)
        rain_total_24.append(sum(rain_change_24))
    fds_rain_24 = [dates.date2num(d) for d in time_rain_24]  # ax_y
    logger.debug(f"rain_total_24: {rain_total_24}")


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

    try:
        hx = f"Heat Index, {heat_index_2[-1]:.1f}\u2109"
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        hx = "none"
        logger.exception(str(e))

    ax_dict = {
        'fig': fig,

        'ax1_title': None,
        'ax1_x1': fds,
        'ax1_y1': temperature,
        'ax1_legend1': f"Temperature, {temperature[-1]:.1f} \u2109",
        'ax1_x2': fds_2,
        'ax1_y2': heat_index_2,
        'ax1_legend2': hx,
        'ax1_legend2a': f"Heat Index, \u2109",

        'ax1_x3': None,
        'ax1_y3': humid,
        'ax1_legend3': f"Humidity {humid[-1]:.0f}%",
        'ax1_xlabel': None,
        'ax1_ylabel': None,

        'ax2_title': None,
        'ax2_x': None,
        'ax2_y': wind,
        'ax2_legend': f"Wind is {wind[-1]:.0f} MPH \nfrom the {compass[wind_direct[-1]]}\nwith Gusts at {gust[-1]:.0f} MPH",
        'ax2_xlabel': None,
        'ax2_ylabel': None,

        'ax3_title': None,
        'ax3_x': None,
        'ax3_y': baro,
        'ax3_legend': f"Barometric Pressure, {baro[-1]:.2f} inch Hg",
        'ax3_xlabel': xlabel,
        'ax3_ylabel': None,

        'ax4_x': fds,
        'ax4_y': rain_change,
        'ax4_y2': rain_total,
        'ax4_y3': rain_total_today,
        'ax4_x3': fds_rain_today,
        'ax4_y4': rain_total_yesterday,
        'ax4_x4': fds_rain_yesterday,
        'ax4_y5': rain_total_24,
        'ax4_x5': fds_rain_24,


    }

    make_ax1(ax_dict)
    make_ax2(ax_dict)
    make_ax3(ax_dict)
    make_ax4(ax_dict)

    pyplot.figtext(0.75, 0.95, f"{time_now}\n", fontsize=20, horizontalalignment='left', verticalalignment='top')

    pyplot.figtext(0.75, 0.10, f"(Last report time: {time[-1]})", fontsize=15, horizontalalignment='left', verticalalignment='top')

    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph.png')
    mng = pyplot.get_current_fig_manager()

    mng.full_screen_toggle()  # full screen no outline

    pyplot.show(block=False)
    pyplot.pause(60)

    pyplot.close(fig="My Figure")

    cursor.close()
    db_connection.close()
    gc.collect()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # set up logging to a file
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M', filename='/temp/MQTTApp.log', filemode='w')
    # define a
    # create a file handler to log to a file
    fh = logging.FileHandler('MQTTApp.log')
    fh.setLevel(logging.DEBUG)
    # create a handler to write to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    # create a formatter and add to handlers
    formatter = logging.Formatter(
        '%(asctime)s - Level Name: %(levelname)s\n  - Message: %(message)s \n  - Function: %(funcName)s - Line: %(lineno)s - Module: %(module)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    one_day()
