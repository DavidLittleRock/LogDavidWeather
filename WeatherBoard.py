import pymysql as mdb
from python_mysql_dbconfig import read_db_config
from WeatherAppLog import get_a_logger
import sys
import Settings
import numpy as np
import gc
from matplotlib import pyplot
from datetime import datetime
from matplotlib import dates
from PIL import Image
import matplotlib
import time


database_table = Settings.database_table
logger = get_a_logger(__name__)

"""
will read data from SQL and make graphs and display graphs
option to save graphs
"""

# TODO add clock, in title? would only update on new graphs
# TODO add last data time

def open_db_connection():
    # this will open a new connection to SQL
    try:
        db_config = read_db_config()
        db_connection = mdb.connect(**db_config)
        if db_connection.open:
            logger.debug(f"db connect open; success with:\n\t{db_config}")
        my_cursor = db_connection.cursor()
        return my_cursor, db_connection
    except:
        # print("fail to connect to database")
        e = sys.exc_info()[0]
        logger.exception(str(e))


def close_db_connection(my_cursor, db_connection):
    # close the SQL connection
    my_cursor.close()
    db_connection.close()
    if not db_connection.open:
        logger.debug(f"db connection closed successfully")


def get_last_id():
    my_cursor, db_connection = open_db_connection()  # open db connection

    query = 'SELECT id FROM OURWEATHERTable ORDER BY id DESC LIMIT 1'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()  # a tuple ((id,),)
# FIXME change from fetchall to get one line
        logger.debug(f"last row id = {result}\n\ttype: {type(result)}")
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result = ((0,),)

    row_id = result[0][0]
    logger.debug(f"row_id to return: {row_id}; \n\ttype: {type(row_id)}")
    close_db_connection(my_cursor, db_connection)  # close the db connection

    return row_id


def get_data():
# TODO make chill factor, in SQL or here?
    my_cursor, db_connection = open_db_connection()  # open db connection
    # DO QUERY
    query = 'SELECT Date, Temp, HI, Humid, Wind, Wind_Direction, BP FROM OneMonth ORDER BY Date ASC'

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()  # a tuple ((id,),)
#        logger.debug(f"last row id = {result}\n\ttype: {type(result)}")
        logger.debug(f"row [0]: {result[0]}\n\ttype: {type(result[0])}")
        logger.debug(f"item[0][0]: {result[0][0]}\n\ttype: {type(result[0][0])}")
        logger.debug(f"item[0][2]: {result[0][1]} \n\ttype: {type(result[0][1])}")
    except:
        e = sys.exc_info()[0]
        print(f"The error is {e}")
        result = ((0,0, ),)

    # QUERY FOR # 30 DAY RAIN
    query = 'SELECT Date, SUM(Rain_Change) FROM OneMonth GROUP BY Day(Date) ORDER BY Date ASC'
    try:
        my_cursor.execute(query)
        result_rain_30 = my_cursor.fetchall()
        logger.debug(f"rain_result_30 query : {result_rain_30}; \n\tif 0, 0 then nothing returned")

    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        result_rain_30 = ((0, 0),)

    # QUERY one day rain BAR
    query = 'SELECT Date, Rain_Change FROM OneDay ORDER BY Date ASC'
    result_rain_bar = ((0, 0,),)

    try:
        my_cursor.execute(query)  # execute a query to select all rows
        result_rain_bar = my_cursor.fetchall()
        logger.debug(f"rain_result_bar query : {result_rain_bar}; \n\tif 0, 0 then nothing returned")

    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    # QUERY rain TODAY
    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Day(Date) = Day(CURDATE()) ORDER BY Date ASC'  # Today start 00:00 to now
    result_rain_today = ((0, 0,),)

    try:
        my_cursor.execute(query)
        result_rain_today = my_cursor.fetchall()
        logger.debug(f"rain_result_today query : {result_rain_today}; \n\tif 0, 0 then nothing returned")
    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

#  QUERY one day rain YESTERDAY
    query = 'SELECT Date, Rain_Change FROM OneMonth WHERE Day(Date) = Day(DATE_SUB(CURDATE(), INTERVAL 1 DAY)) ORDER BY Date ASC'  # Yesterday 00:00 to 00:00
    result_rain_yesterday = ((0, 0,),)

    try:
        my_cursor.execute(query)
        result_rain_yesterday = my_cursor.fetchall()
        logger.debug(f"rain_result_yesterday query : {result_rain_yesterday}; \n\tif 0, 0 then nothing returned")

    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

# QUERY rain 24
    query = 'SELECT Date, Rain_Change FROM OneDay WHERE Date >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR) ORDER BY Date ASC'  # 24 hr rain
    result_rain_24 = ((0, 0,),)

    try:
        my_cursor.execute(query)
        result_rain_24 = my_cursor.fetchall()
        logger.debug(f"rain_result_24 query : {result_rain_24}; \n\tif 0, 0 then nothing returned")

    except:
        e = sys.exc_info()[0]
        print(f"the error is {e}")
        print(f"The error is {sys.exc_info()[0]} : {sys.exc_info()[1]}.")
        logger.exception(str(e))

    close_db_connection(my_cursor, db_connection)  # close the db connection
# Move results into dict of lists
# TODO wind direction
    dict_result = {
        'time'  : [],
        'temp'  : [],
        'hi'    : [],
        'humid' : [],
        'wind'  : [],
        'wind_d': [],
        'bp'    : [],
        'time_hi': [],
        'time_rain_30': [],
        'rain_30': [],
        'rain_30_sum': [],
        'time_rain_yesterday': [],
        'rain_change_yesterday': [],
        'rain_total_yesterday': [],
        'time_rain_bar': [],
        'rain_change_bar': [],
        'time_rain_today': [],
        'rain_change_today': [],
        'rain_total_today': [],
        'time_rain_24': [],
        'rain_change_24': [],
        'rain_total_24': [],
        'rain_7': [],
    }

    for record in result:  # make a list for each measure
        dict_result['time'].append(record[0])
        dict_result['temp'].append(record[1])
        dict_result['hi'].append(record[2])
        dict_result['humid'].append(record[3])
        dict_result['wind'].append(record[4])
        dict_result['wind_d'].append(record[5])
        dict_result['bp'].append(record[6])
        dict_result['time_hi'].append(record[0])

    for record in result_rain_30:
        dict_result['time_rain_30'].append(record[0])
        dict_result['rain_30'].append(record[1] / 22.5)
        dict_result['rain_30_sum'].append(sum(dict_result['rain_30']))

    for record in result_rain_yesterday:
        dict_result['time_rain_yesterday'].append(record[0])
        dict_result['rain_change_yesterday'].append(record[1] / 22.5)
        dict_result['rain_total_yesterday'].append(sum(dict_result['rain_change_yesterday']))

    for record in result_rain_bar:
        dict_result['time_rain_bar'].append(record[0])
        dict_result['rain_change_bar'].append(record[1] / 22.5)

    for record in result_rain_today:
        dict_result['time_rain_today'].append(record[0])
        dict_result['rain_change_today'].append(record[1] / 22.5)
        dict_result['rain_total_today'].append(sum(dict_result['rain_change_today']))

    for record in result_rain_24:
        dict_result['time_rain_24'].append(record[0])
        dict_result['rain_change_24'].append(record[1] / 22.5)
        dict_result['rain_total_24'].append(sum(dict_result['rain_change_24']))

#    convert each list to a numpy array
    for k in dict_result:
        dict_result[k] = np.array(dict_result[k])

    dict_result['hi'] = dict_result['hi'][dict_result['temp'] > 80]  # filter hi for temp > 80
    dict_result['time_hi'] = dict_result['time_hi'][dict_result['temp'] > 80]

#  filter 30 day rain to 7 days
    dict_result['rain_7'] = dict_result['rain_30'][dates.date2num(dict_result['time_rain_30']) > dates.date2num(datetime.now()) - 7]

    gc.collect()

    return dict_result


def make_fig_1(ax_dict):
# figure
    figure_1 = pyplot.figure(num='one', facecolor='green')
    pyplot.suptitle("One Day Graph", fontsize='15', fontweight='bold')
    gs = figure_1.add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline

# ax1  TEMP
    ax1 = figure_1.add_subplot(gs[:5, :4])
    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='-', color='blue', markersize=2.0, label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109")
    if ax_dict['hi'] is not None and len(ax_dict['hi']) > 0:  # if there is a Heat Index in the 30 days
        if ax_dict['time'][-1] == ax_dict['time_hi'][-1]:  # if the last reading has a Heat Index
            logger.debug(f"temp = {ax_dict['temp'][-1]}")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0, label=f"Heat Index {ax_dict['hi'][-1]:.1f}\u2109")
            print(f"time hi: {ax_dict['time_hi'][-1]} \ntype {type(ax_dict['time_hi'][-1])}")
            print(f"datetime {datetime.now()}")
        elif dates.date2num(ax_dict['time_hi'][-1]) > (dates.date2num(datetime.now()))-1:  # if there is a heat index in 1 day
            print("ok")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0, label=f"Heat Index \u2109")
        else:  # if no heat index in this day
            pass
    else:  # if no heat index in 30 day
        # do not print Heat Index line
        pass
    if ax_dict['humid'] is not None:
        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange', label=f"Humidity {ax_dict['humid'][-1]:.0f}%")
    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now()))-1, xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours

    ax1.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)
    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(b=True, which='minor', axis='both', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(b=True, which='major', axis='both', color='#666666', linewidth=1.2, linestyle='-')
    ax1.set_facecolor('#edf7f7')
# TODO set all grids like this

#    ax1.grid(True, which='both', axis='both')

    logger.debug('did make_ax1')

# ax2  WIND
    ax2 = figure_1.add_subplot(gs[6:8, :4])

    ax2.plot(ax_dict['time'], ax_dict['wind'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind'][-1]:.0f} MPH")

    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')

    ax2.set_xlabel('')

    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2)
    ax2.grid(True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')


# ax3  BP
    ax3 = figure_1.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks([], rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['bp'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['bp'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.60, xmin=(dates.date2num(datetime.now())) - 1,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    hfmt = dates.DateFormatter('%m/%d \n %H:%M')
    ax3.xaxis.set_major_formatter(hfmt)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')


# ax4 RAIN
    ax4 = figure_1.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    ax4.xaxis.set_major_locator(dates.HourLocator(interval=6))
    ax4.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_formatter(hfmt)
    # if 1 day
    #  if (ax_dict['title'] == '1 day'):
    ax4.bar(ax_dict['time_rain_bar'], ax_dict['rain_change_bar'], color='blue', width=0.005, label="Rain inches")
    if len(ax_dict['rain_total_today']) > 0:  # today
        logger.debug(f"Rain today: {ax_dict['rain_total_today']}")

        ax4.plot(ax_dict['time_rain_today'], ax_dict['rain_total_today'], marker='o', linestyle='--', color='green', markersize=1, linewidth=4,
                 label=f"Rain {ax_dict['rain_total_today'][-1]:.1f} inches today")
    else:
        ax_dict['rain_total_today'][0] = 0.0  # if nothing in rain today then set a 0.0
        logger.debug(f"rain today set to 0 because len was 0")
    if len(ax_dict['rain_total_yesterday']) > 0:  # yesterday
        logger.debug(f"rain yesterday : {ax_dict['rain_total_yesterday']}")
        ax4.plot(ax_dict['time_rain_yesterday'], ax_dict['rain_total_yesterday'], marker='o', linestyle='--', color='orange', markersize=1, linewidth=2,
                 label=f"Rain {dict_result['rain_total_yesterday'][-1]:.1f} inches yesterday")
    if len(ax_dict['rain_total_24']) > 0:  # 24
        ax4.plot(ax_dict['time_rain_24'], ax_dict['rain_total_24'], marker='o', linestyle='-', color='blue', markersize=1, linewidth=1,
                 label=f"Rain {dict_result['rain_total_24'][-1]:.1f} inches in 24 hours")
    ax4.axis(ymin=0, ymax=((max(max(ax_dict['rain_total_24']), max(ax_dict['rain_total_today']), max(ax_dict['rain_total_yesterday']))) + 1) // 1,
             xmin=(dates.date2num(datetime.now())) - 1, xmax=(dates.date2num(datetime.now())))
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax4.grid(True, which='both', axis='both')

    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True, ncol=1, fontsize=15)
    ax4.set_facecolor('#edf7f7')

#    pyplot.savefig(fname="one_day.png", format='png')


    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline
 #   pyplot.close()


def make_fig_2(ax_dict):
    figure_2 = pyplot.figure(num='two', facecolor='green')
    pyplot.suptitle("7 Days", fontsize='15', fontweight='bold')
    gs = figure_2.add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')

    ax1 = figure_2.add_subplot(gs[:5, :4])
    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='-', color='blue', markersize=2.0,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109")
    if ax_dict['hi'] is not None and len(ax_dict['hi']) > 0:  # if there is a Heat Index in the 30 days
        if ax_dict['time'][-1] == ax_dict['time_hi'][-1]:  # if the last reading has a Heat Index
            logger.debug(f"temp = {ax_dict['temp'][-1]}")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
                     label=f"Heat Index {ax_dict['hi'][-1]:.1f}\u2109")
            print(f"time hi: {ax_dict['time_hi'][-1]} \ntype {type(ax_dict['time_hi'][-1])}")
            print(f"datetime {datetime.now()}")
        elif dates.date2num(ax_dict['time_hi'][-1]) > (
        dates.date2num(datetime.now())) - 1:  # if there is a heat index in 1 day
            print("ok")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
                     label=f"Heat Index \u2109")
        else:  # if no heat index in this day
            pass
    else:  # if no heat index in 30 day
        # do not print Heat Index line
        pass
# block out humid plot
#    if ax_dict['humid'] is not None:
#        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
#                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceding 7 days
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)

    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')

    logger.debug('did make_ax1')
    ax1.set_facecolor('#edf7f7')

# ax2  WIND
    ax2 = figure_2.add_subplot(gs[6:8, :4])

    ax2.plot(ax_dict['time'], ax_dict['wind'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind'][-1]:.0f} MPH")

    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')

    ax2.set_xlabel('')

    ax2.set_ylabel('MPH')
    ax2.grid(b=True, which='both', axis='both')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')

# ax3  BP
    ax3 = figure_2.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks([], rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['bp'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['bp'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.60, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    hfmt = dates.DateFormatter('%m/%d\n%A')
    ax3.xaxis.set_major_formatter(hfmt)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')

# ax4 RAIN
    ax4 = figure_2.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    #    print(ax_dict['y1'])
    i = 0
    for u in ax_dict['rain_30']:
        if u < 0.01:
            ax_dict['rain_30'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

    #    print(ax_dict['y1'])
    ax4.bar(ax_dict['time_rain_30'], ax_dict['rain_30'], color='blue', width=0.99, label=f"Rain {sum(dict_result['rain_7']):0.1f} inches\n this 7 days", align='edge')
    ax4.axis(ymin=0, ymax=(max(ax_dict['rain_30']) + 1) // 1, xmin=(dates.date2num(datetime.now())) - 7,
             xmax=(dates.date2num(datetime.now())))
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1), shadow=True, ncol=1, fontsize=15)
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax4.grid(b=True, which='both', axis='both')

    ax4.set_facecolor('#edf7f7')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def make_fig_3(ax_dict):
    figure_3 = pyplot.figure(num='three', facecolor='green')
    pyplot.suptitle("30 Days", fontsize='15', fontweight='bold')
    gs = figure_3.add_gridspec(10, 5)
    hfmt = dates.DateFormatter('')

    ax1 = figure_3.add_subplot(gs[:5, :4])
    ax1.plot(ax_dict['time'], ax_dict['temp'], marker='o', linestyle='-', color='blue', markersize=2.0,
             label=f"Temp {ax_dict['temp'][-1]:.1f}\u2109")
    if ax_dict['hi'] is not None and len(ax_dict['hi']) > 0:  # if there is a Heat Index in the 30 days
        if ax_dict['time'][-1] == ax_dict['time_hi'][-1]:  # if the last reading has a Heat Index
            logger.debug(f"temp = {ax_dict['temp'][-1]}")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
                     label=f"Heat Index {ax_dict['hi'][-1]:.1f}\u2109")
            print(f"time hi: {ax_dict['time_hi'][-1]} \ntype {type(ax_dict['time_hi'][-1])}")
            print(f"datetime {datetime.now()}")
        elif dates.date2num(ax_dict['time_hi'][-1]) > (
                dates.date2num(datetime.now())) - 1:  # if there is a heat index in 1 day
            print("ok")
            ax1.plot(ax_dict['time_hi'], ax_dict['hi'], marker=6, linestyle='', color='red', markersize=4.0,
                     label=f"Heat Index \u2109")
        else:  # if no heat index in this day
            pass
    else:  # if no heat index in 30 day
        # do not print Heat Index line
        pass
#    if ax_dict['humid'] is not None:
#        ax1.plot(ax_dict['time'], ax_dict['humid'], marker='.', linestyle='', color='orange',
#                 label=f"Humidity {ax_dict['humid'][-1]:.0f}%")

    ax1.axis(ymin=10, ymax=110, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceding 7 days
    ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))
#    ax1.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.xaxis.set_major_formatter(hfmt)

    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')

    logger.debug('did make_ax1')
    ax1.set_facecolor('#edf7f7')

# ax2  WIND
    ax2 = figure_3.add_subplot(gs[6:8, :4])

    ax2.plot(ax_dict['time'], ax_dict['wind'], marker='o', linestyle='-', color='blue', markersize=2, linewidth=0.5,
             label=f"Wind Speed {ax_dict['wind'][-1]:.0f} MPH")

    ax2.axis(ymin=0, ymax=6, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax2.xaxis.set_major_locator(dates.DayLocator(interval=1))
#    ax2.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    ax2.xaxis.set_major_formatter(hfmt)

    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True, ncol=1, fontsize=15)
    ax2.set_title('', fontsize='15')

    ax2.set_xlabel('')

    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')

    ax2.set_facecolor('#edf7f7')

# ax3  BP
    ax3 = figure_3.add_subplot(gs[8:, :4])  # ax3 is local scope but modifies fig that was passed in as argument
    pyplot.xticks(rotation='45')

    ax3.plot(ax_dict['time'], ax_dict['bp'], marker='o', linestyle='-', color='green', markersize=1.5, linewidth=1,
             label=f"BP {ax_dict['bp'][-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.60, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))  # set a rolling x asis for preceeding 24 hours
    ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
#    ax3.xaxis.set_minor_locator(dates.HourLocator(interval=6))
    hfmt = dates.DateFormatter('%m/%d')
    ax3.xaxis.set_major_formatter(hfmt)

    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize=15)
    ax3.set_title('', fontsize='15')
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')

    ax3.set_facecolor('#edf7f7')

# ax4 RAIN
    ax4 = figure_3.add_subplot(gs[5:6, :4])
    pyplot.xticks([], rotation='45')
    hfmt = dates.DateFormatter('')

    ax4.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax4.xaxis.set_major_formatter(hfmt)
    #    print(ax_dict['y1'])
    i = 0
    for u in ax_dict['rain_30']:
        if u < 0.01:
            ax_dict['rain_30'][i] = 0.0
            i += 1
        else:
            i += 1
            continue

    ax4.bar(ax_dict['time_rain_30'], ax_dict['rain_30'], color='blue', width=0.99, label=f"Rain inches,\n {dict_result['rain_30_sum'][-1]:.1f} total this 30 days", align='edge')
    ax4.axis(ymin=0, ymax=(max(ax_dict['rain_30']) + 1) // 1, xmin=(dates.date2num(datetime.now())) - 30,
             xmax=(dates.date2num(datetime.now())))
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1), shadow=True, ncol=1, fontsize=15)
    ax4.set_title('', fontsize='15')
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(b=True, which='major', color='#666666', linewidth=1.2, linestyle='-', axis='both')
 #   ax4.grid(b=True, which='both', axis='both')

    ax4.set_facecolor('#edf7f7')

    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def check_for_new(used_id):
# return False if used_id == get_last_id(), no new data

    last_id = get_last_id()
    if last_id != used_id:
        used_id = last_id
        new_data = True
        dict_result = get_data()
        return used_id, new_data, dict_result
    else:
        new_data = False
        dict_result = get_data()
        return used_id, new_data, dict_result


if __name__ == "__main__":
 #   last_id = get_last_id()
    # loop check last id to see if new
    # if new then get full data
    dict_result = get_data()

    while True:

        make_fig_1(dict_result)

        make_fig_2(dict_result)

        make_fig_3(dict_result)

        used_id = get_last_id()
        new_data = False
        pyplot.figure(num='one')
        while not new_data:
            pyplot.figure(num='one')
   #         pyplot.show(block=False)
            pyplot.pause(5.0)
   #         pyplot.clf()
#            pyplot.figure
#            pyplot.draw()
 #           time.sleep(10)
            pyplot.figure(num='two')
#            pyplot.show(block=False)
            pyplot.pause(5.0)
 #           time.sleep(10)

            pyplot.figure(num='three')
#            pyplot.show(block=False)
            pyplot.pause(5.0)

#            used_id, new_data, dict_result = check_for_new(used_id)
#            if check_for_new(used_id):
            if used_id != get_last_id():
                dict_result = get_data()
                new_data = True

        pyplot.close(fig='all')
