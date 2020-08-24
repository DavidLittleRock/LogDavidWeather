# LogDavidWeather

This is to log and display data from my SwitchDoc Labs weather station. It is based on the SWL 'DataLogger' repository.

Data is sent, published by MQTT from the weatherboard to Mosquitto on a Raspberry Pi 3B+. The MQTTApp.py file will subscribe to the channel and write it to a MariaDB database hosted on the same Pi.
Other python scripts (OneDay.py, OneWeek.py ...) will select data from the database and graph it with MatPlotLib to display on screen. 
When running unattended, I have the Pi HDMI pluged into a spare display so I have a 'dedicated' weather display.
