import gc
import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import dates
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FormatStrFormatter
import pylab
import numpy as np
from numpy import mean
import sys
from pytz import timezone
from httplib2 import http
from datetime import datetime
import pymysql as mdb
import scipy
from scipy import signal

dataBaseName = 'DataLogger'
dataBaseTable = 'OURWEATHERTable'
username = 'datalogger'
password = 'Data0233'
hostname = 'localhost'

db_connection = mdb.connect(hostname, username, password, dataBaseName)
cursor = db_connection.cursor()

query = 'SELECT Date, Temp, HI FROM SevenDayTempHeatIndex ORDER BY Date ASC'

try:
    cursor.execute(query)
    result = cursor.fetchall()
except:
    e = sys.exc_info()[0]
    print(f"the error is {e}")

time = []
temperature = []
heat_index = []

for record in result:
    time.append(record[0])
    temperature.append(record[1])
    heat_index.append(record[2])


fds = [dates.date2num(d) for d in time]
hfmt = dates.DateFormatter('%m/%d - %H')

x = np.array([fds])
y = np.array([heat_index])

x = x[y > 80]  # filter out if heat_index is less than 80
y = y[y > 80]


fig, ax = pyplot.subplots()
pyplot.xticks(rotation='45')
ax.xaxis.set_major_formatter(hfmt)
ax.plot(fds, temperature, marker='o', linestyle='--', color='blue', markersize=2.0)
# ax.plot(fds, heat_index, c='r')
ax.plot(x, y, marker='o', linestyle='', color='orange', markersize=2.0)
ax.axis(ymin=10, ymax=110)

print(temperature[-1])
print(max(temperature))

# ax.annotate('local max', xy=(0.8, 0.2), xycoords='axes fraction', xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='right', verticalalignment='top',)
ax.set_title("Temperature and Heat Index")
pyplot.figtext(0.15, 0.85, f"Temperature now:\n {temperature[-1]:.1f}", horizontalalignment='left', verticalalignment='top')
pyplot.figtext(0.75, 0.85, f"Max: {max(temperature):.1f} \nMin: {min(temperature):.1f} \nAve: {mean(temperature):.1f}", horizontalalignment='left', verticalalignment='top')

ax.set_xlabel("Date")
ax.set_ylabel("degree F")
ax.grid(which='both', axis='both')
pyplot.savefig('/var/www/html/TestGraph.png')

pyplot.show()
