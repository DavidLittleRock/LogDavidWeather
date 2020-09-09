import gc
from matplotlib import pyplot
from matplotlib import dates
import numpy as np
import sys
from datetime import datetime
import pymysql as mdb
import Settings
import logging
from python_mysql_dbconfig import read_db_config


# temperature
def make_ax1(ax_dict):
    gs = ax_dict['fig'].add_gridspec(5, 5)
    hfmt = dates.DateFormatter('')
    ax1 = ax_dict['fig'].add_subplot(gs[:3, :])
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax1.plot(ax_dict['x1'], ax_dict['y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['y1_legend'])
    if ax_dict['y2'] is not None:
        ax1.plot(ax_dict['x2'], ax_dict['y2'], marker='o', linestyle='', color='red', markersize=2.0, label=ax_dict['y2_legend'])
    if ax_dict['y3'] is not None:
        ax1.plot(ax_dict['x3'], ax_dict['y3'], marker='.', linestyle='', color='orange', label=ax_dict['y3_legend'])
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-7, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 7 days
    ax1.legend(shadow=True, ncol=1, fontsize=15)
    ax1.set_title(ax_dict['title'], fontsize='15')
    ax1.set_xlabel(ax_dict['x_label'])
    ax1.set_ylabel(ax_dict['y_label'])
    ax1.grid(which='both', axis='both')


# wind
def make_ax2(ax_dict):
    gs = ax_dict['fig'].add_gridspec(5, 5)
    hfmt = dates.DateFormatter('')
    ax2 = ax_dict['fig'].add_subplot(gs[3:4, :])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(ax_dict['x'], ax_dict['y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=ax_dict['y_legend'])
    ax2.axis(ymin=0, ymax=8, xmin=(dates.date2num(datetime.now()))-7, xmax=(dates.date2num(datetime.now())))
    ax2.legend(shadow=True, ncol=1, fontsize=15)
    ax2.set_title(ax_dict['title'], fontsize='15')
    ax2.set_xlabel(ax_dict['x_label'])
    ax2.set_ylabel(ax_dict['y_label'])
    ax2.grid(which='both', axis='both')


# barometric pressure
def make_ax3(ax_dict):
    """
    Barometric pressure
    Args:
        ax_dict ():
    """
    gs = ax_dict['fig'].add_gridspec(5, 5)
    hfmt = dates.DateFormatter('%m/%d')
    ax3 = ax_dict['fig'].add_subplot(gs[4:, :])
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(ax_dict['x'], ax_dict['y'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1, label=ax_dict['y_legend'])
    ax3.axis(ymin=29.50, ymax=30.35, xmin=(dates.date2num(datetime.now()))-7, xmax=(dates.date2num(datetime.now())))
    ax3.legend(shadow=True, ncol=1, fontsize=15)
    ax3.set_title(ax_dict['title'], fontsize='15')
    ax3.set_xlabel(ax_dict['x_label'])
    ax3.set_ylabel(ax_dict['y_label'])
    ax3.grid(which='both', axis='both')


def one_week():
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind, Wind_Direction FROM OneWeek WHERE MOD(ID, 5) = 0 ORDER BY Date ASC'  # SELECT every 7th
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result = ((0, 0, 0, 0, 0, 0, 0),)

    time = []
    temperature = []
    heat_index = []
    humid = []
    baro = []
    wind = []
    wind_direct = []
    for record in result:
        time.append(record[0])
        temperature.append(record[1])  # ax_x1
        heat_index.append(record[2])
        humid.append(record[3])
        baro.append(record[4])
        wind.append(record[5])
        wind_direct.append(record[6])

    fds = [dates.date2num(d) for d in time]  # ax_y
    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
    temperature_2 = np.array([temperature])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]


    query_report = 'SELECT id, OurWeather_DateTime, Outdoor_Temperature, Outdoor_Humidity, Barometric_Pressure, Current_Wind_Speed, Current_Wind_Direction FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'
    last_report = []
    last_temperature = []
    last_humidity = []
    last_pressure = []
    last_wind_speed = []
    last_wind_direction = []
    try:
        cursor.execute(query_report)
        result_time = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result_time = ((0, 0, 0, 0, 0, 0, 0,),)
    # print(result_time[1])
    for record in result_time:
        last_report.append(record[1])
        last_temperature.append(record[2]*9/5+32)
        last_humidity.append(record[3])
        last_pressure.append(record[4]/3386.4)
        last_wind_speed.append(record[5]*0.621)
        last_wind_direction.append(record[6])


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

    fig = make_fig(time_now, last_report[-1])  # scope of fig is one_day()

    wind_dict = {
        'y': wind,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Wind is {last_wind_speed[-1]:.0f} MPH \nfrom the {compass[last_wind_direction[-1]]}",
    }

    bp_dict = {
        'y': baro,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Barometric Pressure {last_pressure[-1]:.2f} inch Hg",
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
        'y1_legend': f"Temperature, {last_temperature[-1]:.1f} \u2109",
        'y2_legend': hx,
        'y3_legend': f"Humidity {last_humidity[-1]:.0f}%",
    }

    make_ax1(temp_dict)
    make_ax2(wind_dict)
    make_ax3(bp_dict)


    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph.png')
    show_fig(fig)

    db_connection.close()
    gc.collect()


def show_fig(fig):
    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline
    pyplot.show(block=False)
    pyplot.pause(60)
    pyplot.close(fig=103)


def make_fig(time_now, lrtime):
    figure = pyplot.figure(num=103, facecolor='green')  # scope of figure is make_fig()
    pyplot.figtext(0.75, 0.95, f"{time_now}\n", fontsize=20, horizontalalignment='left', verticalalignment='top')
    pyplot.figtext(0.75, 0.05, f"(Last report time: {lrtime})", fontsize=15, horizontalalignment='left', verticalalignment='top')
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
    one_week()
