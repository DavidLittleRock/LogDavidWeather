import gc
from typing import Any
from typing import Dict
from typing import Tuple
from typing import Union

from matplotlib import pyplot
from matplotlib import dates
import numpy as np
import sys
from datetime import datetime
import pymysql as mdb
import logging
from python_mysql_dbconfig import read_db_config

logger = logging.getLogger('ml')


# temperature
def make_ax1(ax_dict):
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax = ax_dict['fig'].add_subplot(gs[:5, :4])
    ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
#    ax.plot(ax_dict['ax1_x1'], ax_dict['ax1_y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['ax1_legend1'])
    ax.plot(ax_dict['x1'], ax_dict['y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['y1_legend'])
    if ax_dict['y2'] is not None:
        logger.debug(f"temp = {ax_dict['y1'][-1]}")
        ax.plot(ax_dict['x2'], ax_dict['y2'], marker=6, linestyle='', color='red', markersize=4.0, label=ax_dict['y2_legend'])
    if ax_dict['y3'] is not None:
        ax.plot(ax_dict['x3'], ax_dict['y3'], marker='.', linestyle='', color='orange', label=ax_dict['y3_legend'])
    ax.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
#    ax.axis(ymin=10, ymax=110, xmin=math.trunc(dates.date2num(datetime.today()))-0, xmax=math.trunc(dates.date2num(datetime.now()))+1)  # set a 24 hour period midnight to midnight
    ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax.set_title(ax_dict['title'], fontsize='15')
    ax.set_xlabel(ax_dict['x_label'])
    ax.set_ylabel(ax_dict['y_label'])
    ax.grid(which='both', axis='both')
    ax.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax.grid(which='major', color='#666666', linewidth=1.2)
    logger.debug('did make_ax1')


# wind
def make_ax2(wind_dict):
    """
    wind

    Args:
        ax_dict ():
    """
    gs = wind_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax2 = wind_dict['fig'].add_subplot(gs[6:8, :4])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(wind_dict['x'], wind_dict['y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=wind_dict['y_legend'])
    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title(wind_dict['title'], fontsize='15')
    ax2.set_xlabel(wind_dict['x_label'])
    ax2.set_ylabel(wind_dict['y_label'])
    ax2.grid(which='both', axis='both')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2)


# barometric Pressure
def make_ax3(bp_dict):
    """
    barometric pressure
    Args:
        bp_dict ():
        ax_dict ():
    """
    gs = bp_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('%m/%d \n %H:%M')
    ax3 = bp_dict['fig'].add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(bp_dict['x'], bp_dict['y'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1, label=bp_dict['y_legend'])
    ax3.axis(ymin=29.50, ymax=30.35, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title(bp_dict['title'], fontsize='15')
    ax3.set_xlabel(bp_dict['x_label'])
    ax3.set_ylabel(bp_dict['y_label'])
    ax3.grid(which='both', axis='both')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2)


# rain
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
    ax4.bar(ax_dict['x1'], ax_dict['y1'],  color='blue', width=0.005, label=ax_dict['y1_legend'])
    if len(ax_dict['y2']) > 0:
        ax4.plot(ax_dict['x2'], ax_dict['y2'], marker='o', linestyle='--', color='green', markersize=1, linewidth=2, label=ax_dict['y2_legend'])
    if len(ax_dict['y3']) > 0:
        ax4.plot(ax_dict['x3'], ax_dict['y3'], marker='o', linestyle='--', color='orange', markersize=1, linewidth=2, label=ax_dict['y3_legend'])
    if len(ax_dict['y4']) > 0:
        ax4.plot(ax_dict['x4'], ax_dict['y4'], marker='o', linestyle='--', color='blue', markersize=1, linewidth=2, label=ax_dict['y4_legend'])
    ax4.axis(ymin=0, ymax= max(ax_dict['y1']), xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))
    ax4.set_title(ax_dict['title'], fontsize='15')
    ax4.grid(which='both', axis='both')
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2)
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True, ncol=1, fontsize=15)


def one_day():

    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')

    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)

    if db_connection.open:   # way to check if sql connected
        logger.debug('connected to database')

    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind, Wind_Direction, Rain_Change, Gust FROM OneDay ORDER BY Date ASC'  # this rain will be 48 Hours, not usefull

    try:
        cursor.execute(query)  # execute a query to select all rows
        result: Union[Tuple, Any] = cursor.fetchall()
#        print(result)
#        print(type(result))
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))
        result = ((0, 0, 0, 0, 0, 0, ),)
    time = []
    temperature = []
    heat_index = []
    humid = []
    baro = []
    wind = []
    wind_direct = []
    rain_change = []
#    rain_total = []
    gust = []
    record: tuple
    for record in result:
        time.append(record[0])
        temperature.append(record[1])  # ax_x1
        heat_index.append(record[2])
        humid.append(record[3])
        baro.append(record[4])
        wind.append(record[5])
        wind_direct.append(record[6])
        rain_change.append(record[7]/22.5)
#        rain_total.append(sum(rain_change))
        gust.append(record[8])
    fds = [dates.date2num(d) for d in time]  # ax_y
    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
    temperature_2 = np.array([temperature])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]
    logger.debug(f"heat_index_2: {heat_index_2}")

    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(DATE_SUB(CURDATE(), INTERVAL 1 DAY)) ORDER BY Date ASC'  # Yesterday 00:00 to 00:00

    try:
        cursor.execute(query)
        result_rain_yesterday = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))
        result_rain_yesterday = ((0, 0,),)
    time_rain_yesterday = []
    rain_change_yesterday = []
    rain_total_yesterday = []
    for record in result_rain_yesterday:
        time_rain_yesterday.append(record[0])
        rain_change_yesterday.append(record[1] / 22.5)
        rain_total_yesterday.append(sum(rain_change_yesterday))
    fds_rain_yesterday = [dates.date2num(d) for d in time_rain_yesterday]  # ax_y

    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(CURDATE()) ORDER BY Date ASC'  # Today start 00:00 to now

    try:
        cursor.execute(query)
        result_rain_today = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))
        result_rain_today = ((0, 0,),)
    time_rain_today = []
    rain_change_today = []
    rain_total_today = []
    for record in result_rain_today:
        time_rain_today.append(record[0])
        rain_change_today.append(record[1] / 22.5)
        rain_total_today.append(sum(rain_change_today))
    fds_rain_today = [dates.date2num(d) for d in time_rain_today]  # ax_y

    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Date >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR) ORDER BY Date ASC'  # 24 hr rain

    try:
        cursor.execute(query)
        result_rain_24 = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))
        result_rain_24 = ((0, 0,),)
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

    if temperature[-1] >= 80:
        try:
            hx = f"Heat Index, {heat_index_2[-1]:.1f}\u2109"
        except:
            e = sys.exc_info()[0]
            print(f"the error is {e}")
            print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
            hx = f"Heat Index, ---\u2109"
            logger.exception(str(e))
    else:
        hx = f"Heat Index, ---\u2109"

    fig = make_fig(time_now, time[-1])  # scope of fig is one_day()


    bp_dict = {
        'y': baro,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Barometric Pressure {baro[-1]:.2f} inch Hg",
    }

    wind_dict = {
        'y': wind,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Wind is {wind[-1]:.0f} MPH \nfrom the {compass[wind_direct[-1]]}\nwith Gusts at {gust[-1]:.0f} MPH",
    }

    temp_dict = {
        'y1': temperature,
        'x1': fds,
        'y2': heat_index_2,
        'x2': fds_2,
        'y3': humid,
        'x3': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y1_legend': f"Temperature, {temperature[-1]:.1f} \u2109",
        'y2_legend': hx,
        'y3_legend': f"Humidity {humid[-1]:.0f}%",
    }

    rain_dict = {
        'y1': rain_change,
        'x1': fds,
        'y2': rain_total_today,
        'x2': fds_rain_today,
        'x3': rain_total_yesterday,
        'y3': fds_rain_yesterday,
        'y4': rain_total_24,
        'x4': fds_rain_24,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y1_legend': "Rain, inches",
        'y2_legend': f"Rain today, {rain_total_today[-1]:.1f} inch",
        'y3_legend': f"Rain yesterday, {rain_total_yesterday[-1]:.1f} inch",
        'y4_legend': f"Rain 24 hours {rain_total_24[-1]:.1f} inch",
    }

    make_ax1(temp_dict)
    make_ax2(wind_dict)
    make_ax3(bp_dict)
    make_ax4(rain_dict)


    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph1.png')
    show_fig(fig)

    cursor.close()
    db_connection.close()
    gc.collect()


def show_fig(fig):
    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline
    pyplot.show(block=False)
    pyplot.pause(60)
    pyplot.clf()
    pyplot.close(fig=102)


def make_fig(time_now, lrtime):
    figure = pyplot.figure(num=102, facecolor='green')  # scope of figure is make_fig()
    pyplot.figtext(0.75, 0.95, f"{time_now}\n", fontsize=20, horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.10, f"(Last report time: {lrtime})", fontsize=15, horizontalalignment='left', verticalalignment='top')
    return figure



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
