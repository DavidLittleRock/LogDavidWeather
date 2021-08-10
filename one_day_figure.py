# import datetime
import time
from calendar import monthrange
from calendar import month
from calendar import month_name
import calendar
from datetime import datetime, date, timedelta
from matplotlib import pyplot
from matplotlib import dates
from matplotlib import ticker as ticker
import pandas as pd
import gc
import sql_to_pd

import psutil
import os
import multiprocessing as mp

from WeatherAppLog import get_a_logger
# from twitterBot import write_text_to_tweet
import twitterBot
import schedule
import send_email

logger = get_a_logger(__name__)
logger.setLevel('INFO')


def usage():
    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2 ** 20)


def make_fig_a(plot_days=1):

    is_raining = False
    df_rain_6, df_rain_5, df_rain_7, df_rain_2, df_rain, df = sql_to_pd.get_data()
    temp_now = df['Temp'].iloc[-1]
    max_temp = (df['Temp'].where(df['Date'] >= (
                pd.to_datetime(datetime.now()) - pd.Timedelta(
            days=plot_days)))).max()
    min_temp = (df['Temp'].where(df['Date'] >= (
                pd.to_datetime(datetime.now()) - pd.Timedelta(
            days=plot_days)))).min()
    max_hi = (df['HI'].where(df['Date'] >= (
                pd.to_datetime(datetime.now()) - pd.Timedelta(
            days=plot_days)))).max()

    if plot_days == 1:
        locator_major = dates.HourLocator(interval=1, byhour=(0, 6, 12, 18))
        locator_minor = dates.HourLocator(interval=1, byhour=(range(1, 25)))
        tick_fmt = '%H:00'
        days_to_plot = pd.Timedelta(hours=24 * plot_days)  # convert days to plot to hours to plot
        graph_title = f"One Day Graph: {datetime.today().date()}"
        image_file = "./figures/fig_1.jpeg"
        ax1_graph = 3  # include HI, WC, Humid in ax_1

        print('raining?')
        print(df_rain_2['Rain_Rate'][-6:])
        print('---')
        print(df_rain_2['Rain_Rate'][-6:-3].sum())
        if df_rain_2['Rain_Rate'][-3:].sum() >= 1.0:
            print('is raining')
            is_raining = True
        if df_rain_2['Rain_Rate'][-3:].sum() >= 1.0 and df_rain_2['Rain_Rate'][
                                                        -6:-3].sum() == 0.0:
            print('just started raining')
            # use send_text_tweet
            # twitterBot.send_text_tweet('It has now started raining in west Little Rock.')
        if df_rain_2['Rain_Rate'][-3:].sum() == 0.0:
            print('is NOT raining')
            is_raining = False
        if df_rain_2['Rain_Rate'][-3:].sum() == 0.0 and df_rain_2['Rain_Rate'][
                                                        -6:-3].sum() > 0.1:
            print('has STOPPED raining')

        # make tweet text for the reply tweet
        tweet_text = f'The temperature in west Little Rock is {temp_now}\u2109, over the past 24 hours the high was {max_temp} and the low was {min_temp}.'
        if max_hi > 81:
            tweet_text += f' The heat index was up to {max_hi}.'
        if is_raining:
            tweet_text += ' It is raining.'
        # print(tweet_text)
        twitterBot.write_text_to_tweet(tweet_text,
                                       file_name='reply_tweet.txt')  # this file is used only in the 'reply'

    elif plot_days == 7:
        locator_major = dates.DayLocator(interval=1)
        locator_minor = dates.HourLocator(interval=1, byhour=(0, 6, 12, 18))
        tick_fmt = '%m/%d'
        days_to_plot = pd.Timedelta(hours=24 * plot_days)
        graph_title = 'Seven day graph'
        image_file = "./figures/fig_2.jpeg"
        ax1_graph = 2
    elif plot_days == 30:
        locator_major = dates.WeekdayLocator(interval=1, byweekday=1)
        locator_minor = dates.DayLocator(interval=1, bymonthday=(range(1, 32)))
        tick_fmt = '%m/%d'
        days_to_plot = pd.Timedelta(hours=24 * plot_days)
        graph_title = '30 day graph'
        image_file = "./figures/fig_3.jpeg"
        ax1_graph = 2

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

    # figure
    figure_1 = pyplot.figure(num='one', facecolor='green', figsize=(18.9, 10.4))
    mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline
    pyplot.suptitle(graph_title, fontsize='15', fontweight='bold')
    gs = figure_1.add_gridspec(10, 5)


    # ax1  TEMP
    ax1 = figure_1.add_subplot(gs[:5, :4])
    pyplot.tight_layout(pad=3.0, h_pad=-1.0)

    ax1.plot(df['Date'], df['Temp'], marker='o', linestyle='',
             color='black', markersize=2.0,
             label=f"Temp {temp_now}\u2109\n(High: {max_temp} Low: {min_temp})")

    if ax1_graph == 3:
        ax1.plot(df['Date'], df['HI'], marker=6, linestyle='', color='red',
             label=f'Heat Index {df["HI"].iloc[-1]}\u2109\n(High: {max_hi})',
             markersize=3)
        ax1.plot(df['Date'], df['Humid'], marker='.', linestyle='',
             color='orange', markersize=3,
             label=f"Humidity {df['Humid'].iloc[-1]:.0f}%")

    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
               ncol=1, fontsize=15)

    # try:
    # if len(wc_dict['wind_chill']) >= 1 and dates.date2num(
    #     wc_dict['time_wind_chill'][-1]) > (
    #     dates.date2num(datetime.now())) - 1:
    # ax1.plot(wc_dict['time_wind_chill'], wc_dict['wind_chill'],
    #          marker='v', linestyle='', color='blue',
    #          label='Wind chill')
    # except IndexError as iee:
    #     logger.error(f"failed to plot wind chill Error: {iee}")
    # ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
    #            ncol=1, fontsize=15)

    ax1.axis(ymin=10, ymax=110, xmin=(pd.to_datetime(datetime.now()) - days_to_plot),
             xmax=(pd.to_datetime(datetime.now())))

    # style_ax1(ax1)
    ax1.xaxis.set_major_formatter(dates.DateFormatter(''))  # matplotlib dates
    ax1.set_title('', fontsize='10', fontweight='normal')
    ax1.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
               ncol=1, fontsize=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    ax1.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax1.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax1.grid(b=True, which='both', axis='both')
    ax1.set_facecolor('#edf7f7')

    ax1.xaxis.set_minor_locator(locator_minor)
    ax1.xaxis.set_major_locator(locator_major)

    # if plot_days == 1:
        # tweet text, temp now, max temp today, min temp today, max heat index today


    # logger.debug('did make_ax1 in figure 1')

    # ax2  WIND
    # gust period
    # max_temp = (df_temp['Temp'].where(df_temp['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(days=plot_days)))).max()

    max_gust = (df['Gust'].where(df['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(days=plot_days)))).max()
    max_wind = (df['Wind'].where(df['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(days=plot_days)))).max()

    ax2 = figure_1.add_subplot(gs[6:8, :4])

    ax2.plot(df['Date'], df['Wind'], marker='o', linestyle='-',
             color='black', markersize=2, linewidth=0.5,
             label=f"Wind Speed {df['Wind'].iloc[-1]:.0f} MPH\nfrom the "
                   f"{compass[df['Wind_Direction'].iloc[-1]]}\ngusting between\n{df['Gust'].iloc[-1]:.0f} "
                   f"and {max_gust:.0f} MPH")

    # ax2.plot(df_wind['Date'], df_wind['Gust'], marker='o', linestyle='-',
    #         color='orange',
    #         markersize=2, linewidth=0.5,
    #         label=f"Gust")

    ax2.axis(ymin=0, ymax=max_wind + 0.5, xmin=(pd.to_datetime(datetime.now()) - days_to_plot),
         xmax=(pd.to_datetime(datetime.now())))   # set a rolling x axis for preceding 24 hours

    # style_ax2(ax2)

    ax2.xaxis.set_major_formatter(dates.DateFormatter(''))
    ax2.set_title('', fontsize='15')
    ax2.legend(loc='upper left', bbox_to_anchor=(1.0, 0.9), shadow=True,
               ncol=1, fontsize=15)
    ax2.set_xlabel('')
    ax2.set_ylabel('MPH')
    ax2.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax2.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax2.grid(b=True, which='both', axis='both')
    ax2.set_facecolor('#edf7f7')
    ax2.xaxis.set_major_locator(locator_major)
    ax2.xaxis.set_minor_locator(locator_minor)

    # ax2.xaxis.set_major_locator(dates.HourLocator(interval=6))
    #   gust_period = ax_dict['gust'][dates.date2num(ax_dict['time']) > dates.date2num(
    #    datetime.now()) - 0.25]
    # send_email(subject="ERROR",
    #            message=f"The error is: {ve}. There is no data in the ax_dict['gust'] so is ste "
    #                    f"to 0 for fig 1.")

    ax3 = figure_1.add_subplot(gs[8:, :4])
    # ax3 is local scope but modifies fig that was passed in as argument
    #  pyplot.xticks([], rotation='45')
    #
    ax3.plot(df['Date'], df['BP'], marker='o', linestyle='',
             color='green', markersize=2.0, linewidth=1,
             label=f"BP {df['BP'].iloc[-1]:.2f} mmHg")

    ax3.axis(ymin=29.50, ymax=30.71, xmin=(pd.to_datetime(datetime.now()) - days_to_plot),
         xmax=(pd.to_datetime(datetime.now())))   # set a rolling x axis for preceding 24 hours
    #  ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))

    # style_ax3(ax3)
    # ax3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d'))
    ax3.set_title('', fontsize='15')
    ax3.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), shadow=True,
               ncol=1, fontsize=15)
    ax3.set_xlabel('')
    ax3.set_ylabel('mmHg')
    ax3.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax3.grid(which='major', color='#666666', linewidth=1.2, linestyle='-')
    ax3.grid(b=True, which='both', axis='both')
    ax3.set_facecolor('#edf7f7')
    # ax3.xaxis.set_major_locator(dates.DayLocator(interval=1))
    # ax3.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax3.xaxis.set_major_locator(locator_major)
    ax3.xaxis.set_minor_locator(locator_minor)
    #    ax3.xticks(fontsize=16)
    #    ax3.xlabel(fontdict={'size': 16})
    ax3.tick_params(axis='x', labelsize=16)
    ax3.xaxis.set_major_formatter(dates.DateFormatter(tick_fmt))  # '%m/%d\n%H:00'))

    # ax3.xaxis.set_major_locator(dates.HourLocator(interval=6))

    # ax4 RAIN
    ax4 = figure_1.add_subplot(gs[5:6, :4])

    rain_sum = df_rain_6['Rain_Change'].cumsum()/22.5
    try:
        rain_today = rain_sum.iloc[-1]
    except:
        rain_today = 0.0
    # print(rain_sum)
    ax4.plot(df_rain['Date'], df_rain['cs']/22.5,
             marker='o', linestyle='-', color='green', markersize=1, linewidth=2,
             label=f"Rain {df_rain['cs'].iloc[-1]/22.5:.1f} inches today")  # {rain_sum.iloc[-1]:.1f}
    rain_yest_sum = df_rain_5['Rain_Change'].cumsum()/22.5
    # print(rain_yest_sum)
    ax4.plot(df_rain_5['Date'], df_rain_5['Rain_Sum'],
             marker='o', linestyle='-', color='blue', markersize=1, linewidth=2,
             label=f"Rain {rain_yest_sum.iloc[-1]:.1f} inches yesterday")
    rain_24_sum = df_rain_7['Rain_Change'].cumsum()/22.5
    # print(rain_24_sum)
    ax4.plot(df_rain_7['Date'], df_rain_7['Rain_Sum'],
             marker='o', linestyle='-', color='red', markersize=1, linewidth=2,
             label=f"Rain {rain_24_sum.iloc[-1]:.1f} inches 24 hours")
    # may be able to pull df_rain_2 OUT
    ax4.plot(df_rain_2['Date'], df_rain_2['Rain_Rate'], marker='s',
             linestyle='', color='blue', markersize=4, linewidth=1,
             label="Rain Rate, inch / hr")
    ax4.plot(df_rain['Date'], df_rain['Rain_Rate'], marker='s',
             linestyle='', color='red', markersize=3, linewidth=1,
             label="Rain Rate, inch / hr")

    ymax = df_rain_2['Rain_Rate'].max()+0.1
    print('rain ymax')
    print(ymax)

    ax4.axis(ymin=0, ymax=ymax, xmin=(pd.to_datetime(datetime.now()) - days_to_plot),
             xmax=(pd.to_datetime(datetime.now())))   # set a rolling x axis for preceding 24 hours

    ax4.xaxis.set_major_formatter(dates.DateFormatter(''))
    ax4.set_title('', fontsize='15')
    ax4.legend(loc='upper left', bbox_to_anchor=(1.0, 1.6), shadow=True,
               ncol=1, fontsize=15)
    ax4.set_xlabel('')
    ax4.set_ylabel("inches")
    ax4.grid(which='minor', color='#999999', alpha=0.5, linestyle='--')
    ax4.grid(b=True, which='major', color='#666666', linewidth=1.2,
             linestyle='-', axis='both')
    ax4.grid(b=True, which='both', axis='both')
    ax4.set_facecolor('#edf7f7')
    ax4.xaxis.set_major_locator(locator_major)
    ax4.xaxis.set_minor_locator(locator_minor)

    # ax4.xaxis.set_major_locator(dates.HourLocator(interval=6))

    pyplot.savefig(fname=image_file, format='jpeg')

    #     mng = pyplot.get_current_fig_manager()
    mng.full_screen_toggle()  # full screen no outline


def make_high_temp_tweet():
    """
    this will put high temp today in file daily_high_temp.txt
    tweeted on schedule
    Returns:

    """
    df = sql_to_pd.get_temp_data()
    plot_days = 1
    max_temp = (df['Temp'].where(df['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(days=plot_days)))).max()
    status = f'The high temp I recorded today was {max_temp}\u2109 in Little Rock'
    # twitterBot.send_text_tweet(status)
    twitterBot.write_text_to_tweet(string=status, file_name='daily_high_temp.txt')
    # print(status)
    return status


def make_low_temp_tweet():
    """
    this will put high temp today in file daily_low_temp.txt
    tweeted out on schedule
    Returns:

    """
    df = sql_to_pd.get_temp_data()
    plot_days = 1
    min_temp = (df['Temp'].where(df['Date'] >= (pd.to_datetime(datetime.now()) - pd.Timedelta(days=plot_days)))).min()
    status = f'The low temp I recorded today was {min_temp}\u2109 in west Little Rock'
    # twitterBot.send_text_tweet(status)
    twitterBot.write_text_to_tweet(string=status, file_name='daily_low_temp.txt')
    # print(status)
    return status


def high_temp_yesterday():
    df_rain_6, df_rain_5, df_rain_7, df_rain_2, df_rain, df = sql_to_pd.get_data()

    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())

    df = (df[df['Date'] >= (
        yesterday_midnight)])  # yesterday midnight to now, yesterday plus today so far NOT PLOTED
    df = (df[df['Date'] <= (
        today_midnight)])  # yesterday midnight to today midnight , so 'yesterday'

    max_temp = df['Temp'].max()

    return max_temp


def low_temp_yesterday():
    df_rain_6, df_rain_5, df_rain_7, df_rain_2, df_rain, df = sql_to_pd.get_data()

    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    today_midnight = datetime.combine(today, datetime.min.time())

    df = (df[df['Date'] >= (
        yesterday_midnight)])  # yesterday midnight to now, yesterday plus today so far NOT PLOTED
    df = (df[df['Date'] <= (
        today_midnight)])  # yesterday midnight to today midnight , so 'yesterday'

    min_temp = df['Temp'].min()

    return min_temp


def make_blog_posts():
    # dict_result, hi_dict, wc_result, rain_result = get_data_a()  # get data from SQL
    df_rain_6, df_rain_5, df_rain_7, df_rain_2, df_rain, df = sql_to_pd.get_data()

    print('new day is true, should see daily blog post')
    today = date.today()
    # yesterday = today - timedelta(days=1)
    # yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    # temp_yesterday = []
    # temp_yesterday = dict_result['temp'][
    #     (dict_result['time']) > yesterday_midnight]
    rain_yest_sum = df_rain_5['Rain_Change'].cumsum()/22.5

    max_temp, min_temp, max_hi = sql_to_pd.get_yesterday_data()
    max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp = sql_to_pd.get_year_data()
    string_blog = f"The high yesterday was {max_temp} " \
                  f"and the low was {min_temp}\u2109.\n" \
                  f"There was {rain_yest_sum.iloc[-1]:.1f} " \
                  f"inches of rain.\n"

    if max_hi >= 81:
        string_blog += f"The max heat index yesterday was {max_hi}\u2109.\n"

    string_blog += f"\nThe high temperature so far this year was {max_temp_for_year:.1f}\u2109 " \
                   f"on {custom_date_max_temp} and the low was {min_temp_for_year:.1f} on {custom_date_min_temp}.\n\n" \
                   f"Time : {datetime.now().time()}"

    subject = f"Daily weather post for {datetime.today().date()} [Weather] [Daily]"
    attach = './figures/fig_1.jpeg'
    send_email.write_text_to_send(string_blog, file_name='daily_blog_post.txt')

    send_email.send_blog(message=send_email.read_text_to_send(file_name='daily_blog_post.txt'),
              subject=subject, file=attach)

    if today.day == 1:  # set as 1 for first day of month
        print('first of month is true, should see monthly blog post')
        # modify so is a monthly report
        # print("this is the first day of the month.")
        last_month = monthrange(today.year, today.month - 1)  # a tuple (# day of week for first day, # days)
        max_temp_for_month, custom_date_max_temp, min_temp_for_month, custom_date_min_temp = sql_to_pd.get_last_month_data(today.month - 1)
        string_blog = f"Today is start of {calendar.month_name[today.month]}.\n\n" \
                      f"Last month the high temperature was {max_temp_for_month:.1f}\u2109 " \
                      f"on {custom_date_max_temp} and " \
                      f"the low was {min_temp_for_month:.1f} on {custom_date_min_temp}.\n\n" \
                      f"Time : {datetime.now().time()}"

        subject = f"Weather summary for {calendar.month_name[today.month - 1]} [Weather] [Monthly]"
        attach = './figures/fig_3.jpg'
        send_email.write_text_to_send(string_blog, file_name='monthly_blog_post.txt')
        send_email.send_blog(
            message=send_email.read_text_to_send(file_name='monthly_blog_post.txt'),
            subject=subject, file=attach)

    if datetime.today().weekday() == 0:  # if today is Monday 0. sunday 7
        print('new week is true, should see weekly blog post')
        max_temp_for_week, custom_date_max_temp, min_temp_for_week, custom_date_min_temp = sql_to_pd.get_last_week_data()
        string_blog = f"Today is start of new week.\n\n" \
                      f"Last week the high temperature was {max_temp_for_week:.1f}\u2109 " \
                      f"on {custom_date_max_temp} and " \
                      f"the low was {min_temp_for_week:.1f} on {custom_date_min_temp}.\n\n" \
                      f"Time : {datetime.now().time()}"

        subject = 'Weekly post [Weather] [Weekly]'
        attach = './figures/fig_2.jpeg'
        send_email.write_text_to_send(string_blog, file_name='weekly_blog_post.txt')
        print(string_blog)
        send_email.send_blog(message=send_email.read_text_to_send(file_name='weekly_blog_post.txt'),
                  subject=subject, file=attach)

    return True


def make_email_posts():
    # dict_result, hi_dict, wc_result, rain_result = get_data_a()  # get data from SQL
    df_rain_6, df_rain_5, df_rain_7, df_rain_2, df_rain, df = sql_to_pd.get_data()

    print('new day is true, should see daily email post')
    today = date.today()
    # yesterday = today - timedelta(days=1)
    # yesterday_midnight = datetime.combine(yesterday, datetime.min.time())
    # temp_yesterday = []
    # temp_yesterday = dict_result['temp'][
    #     (dict_result['time']) > yesterday_midnight]
    rain_yest_sum = df_rain_5['Rain_Change'].cumsum()/22.5

    max_temp, min_temp, max_hi = sql_to_pd.get_yesterday_data()
    max_temp_for_year, custom_date_max_temp, min_temp_for_year, custom_date_min_temp = sql_to_pd.get_year_data()
    string_email = f"The high yesterday was {max_temp} " \
                  f"and the low was {min_temp}\u2109.\n" \
                  f"There was {rain_yest_sum.iloc[-1]:.1f} " \
                  f"inches of rain.\n"

    if max_hi >= 81:
        string_email += f"The max heat index yesterday was {max_hi}\u2109.\n"

    string_email += f"\nThe high temperature so far this year was {max_temp_for_year:.1f}\u2109 " \
                   f"on {custom_date_max_temp} and the low was {min_temp_for_year:.1f} on {custom_date_min_temp}.\n\n" \
                   f"Time : {datetime.now().time()}"

    subject = f"Daily weather email for {datetime.today().date()}."
    attach = './figures/fig_1.jpeg'
    send_email.write_text_to_send(string_email, file_name='daily_email.txt')

    send_email.send_email(message=send_email.read_text_to_send(file_name='daily_email.txt'),
              subject=subject, file=attach)

    if today.day == 1:  # set as 1 for first day of month
        print('first of month is true, should see monthly email post')
        # modify so is a monthly report
        # print("this is the first day of the month.")
        last_month = monthrange(today.year, today.month - 1)  # a tuple (# day of week for first day, # days)
        max_temp_for_month, custom_date_max_temp, min_temp_for_month, custom_date_min_temp = sql_to_pd.get_last_month_data(today.month - 1)
        string_email = f"Today is start of {calendar.month_name[today.month]}.\n\n" \
                      f"Last month the high temperature was {max_temp_for_month:.1f}\u2109 " \
                      f"on {custom_date_max_temp} and " \
                      f"the low was {min_temp_for_month:.1f} on {custom_date_min_temp}.\n\n" \
                      f"Time : {datetime.now().time()}"

        subject = f"Weather summary for {calendar.month_name[today.month - 1]}."
        attach = './figures/fig_3.jpg'
        send_email.write_text_to_send(string_email, file_name='monthly_email.txt')
        send_email.send_email(
            message=send_email.read_text_to_send(file_name='monthly_email.txt'),
            subject=subject, file=attach)

    if datetime.today().weekday() == 0:  # if today is Monday 0. sunday 7
        print('new week is true, should see weekly email post')
        max_temp_for_week, custom_date_max_temp, min_temp_for_week, custom_date_min_temp = sql_to_pd.get_last_week_data()
        string_email = f"Today is start of new week.\n\n" \
                      f"Last week the high temperature was {max_temp_for_week:.1f}\u2109 " \
                      f"on {custom_date_max_temp} and " \
                      f"the low was {min_temp_for_week:.1f} on {custom_date_min_temp}.\n\n" \
                      f"Time : {datetime.now().time()}"

        subject = 'Weekly weather email.'
        attach = './figures/fig_2.jpg'
        send_email.write_text_to_send(string_email, file_name='weekly_email.txt')
        print(string_email)
        send_email.send_email(message=send_email.read_text_to_send(file_name='weekly_email.txt'),
                  subject=subject, file=attach)

    return True


if __name__ == '__main__':
    pyplot.close(fig='all')
    mp.set_start_method('spawn')
    schedule.every(2).minutes.do(twitterBot.send_reply_tweet)
    schedule.every(10).minutes.do(twitterBot.follow_followers)
    schedule.every(15).minutes.do(twitterBot.get_incoming_tweets)
    schedule.every().day.at('15:35').do(twitterBot.send_text_tweet, text=twitterBot.read_text_to_tweet('daily_high_temp.txt'))
    schedule.every().day.at('08:30').do(twitterBot.send_text_tweet, text=twitterBot.read_text_to_tweet('daily_low_temp.txt'))
    schedule.every().day.at('00:15').do(make_blog_posts)
    schedule.every().day.at('00:30').do(make_email_posts)

    while True:
        p1 = mp.Process(target=make_fig_a, args=(1,))
        p1.start()
        p1.join()
        p1.close()
        # make_fig_a(1)
        pyplot.close(fig='all')

        # make_fig_a(7)
        p2 = mp.Process(target=make_fig_a, args=(7,))
        p2.start()
        p2.join()
        p2.close()
        pyplot.close(fig='all')

        # make_fig_a(30)
        p3 = mp.Process(target=make_fig_a, args=(30,))
        p3.start()
        p3.join()
        p3.close()
        pyplot.close(fig='all')

        # twitterBot.main()  # will this block here??
        make_high_temp_tweet()
        make_low_temp_tweet()
        schedule.run_pending()

        gc.collect()
        print('usage after gc')
        print(usage())
        time.sleep(110)

