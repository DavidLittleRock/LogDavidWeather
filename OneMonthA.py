import gc
from matplotlib import pyplot
from matplotlib import dates
import numpy as np
import sys
from datetime import datetime
import pymysql as mdb
import Settings
from python_mysql_dbconfig import read_db_config
import logging
from WeatherAppLog import get_a_logger

# logger = logging.getLogger('ml')
logger = get_a_logger(__name__)



def get_temperature_data(fig):
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
    #    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp FROM OneMonth WHERE MOD(ID, 7) = 0 ORDER BY Date ASC'  # SELECT every 10th
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result = ((0, 0,),)

    query_report = 'SELECT id, OurWeather_DateTime, Outdoor_Temperature FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'

    try:
        cursor.execute(query_report)
        result_time = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result_time = ((0, 0,),)

    cursor.close()
    db_connection.close()

    time = []
    temperature = []

    for record in result:
        time.append(record[0])
        temperature.append(record[1])  # ax_x1

    fds = [dates.date2num(d) for d in time]  # ax_y

    last_report = []
    last_temperature = []

    for record in result_time:
        last_report.append(record[1])
        last_temperature.append(record[2] * 9 / 5 + 32)

    temp_dict = {
        'y1': temperature,
        'x1': fds,
        'y2': None,
        'x2': None,
        'y3': None,
        'x3': None,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y1_legend': f"Temperature, {last_temperature[-1]:.1f} \u2109",
        'y2_legend': None,
        'y3_legend': None,
        'last_report': last_report[-1],
    }

    gc.collect()

    return temp_dict


def get_wind(fig):
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()
    query = 'SELECT Date, Wind, Wind_Direction FROM OneMonth WHERE MOD(ID, 7) = 0 ORDER BY Date ASC'  # SELECT every 10th
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result = ((0, 0, 0,),)
    time = []
    wind = []
    wind_direct = []
    for record in result:
        time.append(record[0])
        wind.append(record[1])
        wind_direct.append(record[2])

    fds = [dates.date2num(d) for d in time]  # ax_y

    query_report = 'SELECT id, OurWeather_DateTime, Current_Wind_Speed, Current_Wind_Direction FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'

    try:
        cursor.execute(query_report)
        result_time = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result_time = ((0, 0, 0, 0,),)

    cursor.close()
    db_connection.close()

    last_report = []
    last_wind_speed = []
    last_wind_direction = []

    for record in result_time:
        last_report.append(record[1])
        last_wind_speed.append(record[2] * 0.621)
        last_wind_direction.append(record[3])

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

    wind_dict = {
        'y': wind,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Wind is {last_wind_speed[-1]:.0f} MPH \nfrom the {compass[last_wind_direction[-1]]}",
    }

    return wind_dict


def get_bp_data(fig):
    """
    get data from DB and put into a dict
    Args:
        fig ():

    Returns:
        bp_dict

    """
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
    #    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()
    query = 'SELECT Date, BP FROM OneMonth WHERE MOD(ID, 7) = 0 ORDER BY Date ASC'  # SELECT every 10th
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result = ((0, 0,),)

    query_report = 'SELECT id, OurWeather_DateTime, Barometric_pressure FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'

    try:
        cursor.execute(query_report)
        result_time = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result_time = ((0, 0,),)

    cursor.close()
    db_connection.close()

    time = []
    baro = []
    for record in result:
        time.append(record[0])
        baro.append(record[1])

    fds = [dates.date2num(d) for d in time]  # ax_y

    last_report = []
    last_pressure = []
    for record in result_time:
        last_report.append(record[1])
        last_pressure.append(record[2] / 3386.4)

    bp_dict = {
        'y': baro,
        'x': fds,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y_legend': f"Barometric Pressure {last_pressure[-1]:.2f} inch Hg",
    }

    gc.collect()

    return bp_dict


def get_rain(fig):
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
    #    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()

    query = 'SELECT Date, SUM(Rain_Change) FROM OneMonth GROUP BY Day(Date) ORDER BY Date ASC'
    try:
        cursor.execute(query)
        result_rain = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result_rain = ((0, 0),)
    cursor.close()
    db_connection.close()
    time_rain = []
    rain = []
    for record in result_rain:
        time_rain.append(record[0])
        rain.append(record[1] / 22.5)
#    x6 = time_rain
#    y6 = rain
    rain_total = sum(rain)

    rain_dict = {
        'y1': rain,
        'x1': time_rain,
        #        'y2': rain_total_today,
        #        'x2': fds_rain_today,
        #        'x3': rain_total_yesterday,
        #        'y3': fds_rain_yesterday,
        #        'y4': rain_total_24,
        #        'x4': fds_rain_24,
        'fig': fig,
        'title': None,
        'x_label': None,
        'y_label': None,
        'y1_legend': f"Rain {rain_total:.1f} inches this month",
        #        'y2_legend': f"Rain today, {rain_total_today[-1]:.1f} inch",
        #        'y3_legend': f"Rain yesterday, {rain_total_yesterday[-1]:.1f} inch",
        #        'y4_legend': f"Rain 24 hours {rain_total_24[-1]:.1f} inch",
    }

    return rain_dict


# temperature
def make_ax1(ax_dict):
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax1 = ax_dict['fig'].add_subplot(gs[:5, :])
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax1.plot(ax_dict['x1'], ax_dict['y1'], marker='o', linestyle='-', color='blue', markersize=2.0, label=ax_dict['y1_legend'])
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 30 days
    ax1.legend(shadow=True, ncol=1, fontsize=15)
    ax1.set_title(ax_dict['title'], fontsize='15')
    ax1.set_xlabel(ax_dict['x_label'])
    ax1.set_ylabel(ax_dict['y_label'])
    ax1.grid(which='both', axis='both')
    ax1.set_facecolor('#edf7f7')
    pyplot.figtext(0.75, 0.05, f"(Last report time: {ax_dict['last_report']})", fontsize=15, horizontalalignment='left', verticalalignment='top')


# wind
def make_ax2(ax_dict):  # wind
    gs = ax_dict['fig'].add_gridspec(10, 5)

    hfmt = dates.DateFormatter('')
    ax2 = ax_dict['fig'].add_subplot(gs[6:8, :])
    pyplot.xticks(rotation='45')
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    ax2.plot(ax_dict['x'], ax_dict['y'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5, label=ax_dict['y_legend'])
    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax2.legend(shadow=True, ncol=1, fontsize=15)
    ax2.set_title(ax_dict['title'], fontsize='15')
    ax2.set_xlabel(ax_dict['x_label'])
    ax2.set_ylabel(ax_dict['y_label'])
    ax2.grid(which='both', axis='both')
    ax2.set_facecolor('#edf7f7')


# barometric pressure
def make_ax3(ax_dict):  # barometric pressure
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('%m/\n%d')
    ax3 = ax_dict['fig'].add_subplot(gs[8:, :])
    pyplot.xticks([], rotation='45')
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_major_formatter(hfmt)
    ax3.plot(ax_dict['x'], ax_dict['y'], marker='o', linestyle='-', color='green', markersize=1, linewidth=0.5, label=ax_dict['y_legend'])
    ax3.axis(ymin=29.50, ymax=30.35, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax3.legend(shadow=True, ncol=1, fontsize=15)
    ax3.set_title(ax_dict['title'], fontsize='15')
    ax3.set_xlabel(ax_dict['x_label'])
    ax3.set_ylabel(ax_dict['y_label'])
    ax3.grid(which='both', axis='both')
    ax3.set_facecolor('#edf7f7')


# rain
def make_ax4(ax_dict):
    gs = ax_dict['fig'].add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')
    ax4 = ax_dict['fig'].add_subplot(gs[5:6, :])
    pyplot.xticks([], rotation='45')
    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
#    print(ax_dict['y1'])
    i = 0
    for u in ax_dict['y1']:
        if u < 0.01:
            ax_dict['y1'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

#    print(ax_dict['y1'])
    ax4.bar(ax_dict['x1'], ax_dict['y1'],  color='blue', width=0.99, label=ax_dict['y1_legend'], align='edge')
    ax4.axis(ymin=0, ymax=(max(ax_dict['y1'])+1)//1, xmin=(dates.date2num(datetime.now()))-30, xmax=(dates.date2num(datetime.now())))
    ax4.legend(shadow=True, ncol=1, fontsize=15)
    ax4.set_title(ax_dict['title'], fontsize='15')
    ax4.grid(which='both', axis='both')
    ax4.set_facecolor('#edf7f7')


def one_month():
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
#    time = datetime.strftime(datetime.now(), '%H:%M, %A')


    """
    db_config = read_db_config()
    # make connection to database
    db_connection = mdb.connect(**db_config)
    database_table = Settings.database_table
#    ax_dict = {}
    time_now = datetime.strftime(datetime.now(), '%H:%M, %A')
    cursor = db_connection.cursor()
    query = 'SELECT Date, Temp, HI, Humid, BP, Wind, Wind_Direction FROM OneMonth WHERE MOD(ID, 7) = 0 ORDER BY Date ASC'  # SELECT every 10th
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

#    temp_now = temperature[-1]
#   max_temp = max(temperature)
#    min_temp = min(temperature)
#    humid_now = humid[-1]
#    baro_now = baro[-1]
    temperature_2 = np.array([temperature])

    fds = [dates.date2num(d) for d in time]  # ax_y

    fds_2 = np.array([fds])
    heat_index_2 = np.array([heat_index])
    fds_2 = fds_2[temperature_2 > 80]  # filter out if temperature is less than 80
    heat_index_2 = heat_index_2[temperature_2 > 80]


    query = 'SELECT Date, SUM(Rain_Change) FROM OneMonth GROUP BY Day(Date) ORDER BY Date ASC'
    try:
        cursor.execute(query)
        result_rain = cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result_rain = ((0, 0), )
    time_rain = []
    rain = []
    for record in result_rain:
        time_rain.append(record[0])
        rain.append(record[1]/22.5)
    x6 = time_rain
    y6 = rain
    rain_total = sum(y6)

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
        last_temperature.append(record[2] * 9 / 5 + 32)
        last_humidity.append(record[3])
        last_pressure.append(record[4] / 3386.4)
        last_wind_speed.append(record[5] * 0.621)
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
    }"""
#    fig = make_fig(time_now, time[-1])  # scope of fig is one_day()
    fig = make_fig(time_now)  # scope of fig is one_day()

    temp_dict = get_temperature_data(fig)

    bp_dict = get_bp_data(fig)

    rain_dict = get_rain(fig)

    wind_dict = get_wind(fig)

    make_ax1(temp_dict)
    make_ax2(wind_dict)
    make_ax3(bp_dict)
    make_ax4(rain_dict)
    pyplot.savefig('/var/www/html/TempHeatIndexSevenDayGraph.png')

    show_fig(fig)


#    cursor.close()
#    db_connection.close()
    gc.collect()


def show_fig(fig):

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline

    pyplot.close(fig=103)
    pyplot.close(fig=102)

    pyplot.show(block=False)
    pyplot.pause(10)


def make_fig(time_now):
    figure = pyplot.figure(num=104, facecolor='green')  # scope of figure is make_fig()
    pyplot.figtext(0.75, 0.95, f"30 Days --  {time_now}\n", fontsize=20, horizontalalignment='left', verticalalignment='top')
#    pyplot.figtext(0.75, 0.05, f"(Last report time: {lrtime})", fontsize=15, horizontalalignment='left', verticalalignment='top')
    return figure


if __name__ == '__main__':

    """
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
    """

    one_month()
