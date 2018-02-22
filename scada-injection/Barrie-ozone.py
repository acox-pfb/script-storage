#!/usr/bin/python
"""
API call to return air quality data for injecting into DATA sensors
"""
import requests
import subprocess
import time

#url = "http://api.waqi.info/feed/shanghai/?token=9e3c71cd65c5c7c01be0e9bac32108a7240b578f"
#data = requests.get(url).json
#print data
params = (
    ('token', '9e3c71cd65c5c7c01be0e9bac32108a7240b578f'),
)

response = requests.get('http://api.waqi.info/feed/Barrie/', params=params)
#print response.content

data = response.content.split(',')
temp = data[18]
humidity = data[20]
ozone = data[16]
#print temp, humidity, ozone

ozone = ozone.split(':')
#print temp[2][:-1]

cmd="/opt/omniai/bin/scadactl -c push "
sensor_id = "1139"
i=1
clock = 500000
wait = 10

while i <= clock:
	epoch_time = str(int(time.time()))+"000000"
	scadactl_cmd1 = cmd + sensor_id + " " + str(ozone[2][:-1]) + " " +  epoch_time
	subprocess.Popen(scadactl_cmd1,shell=True)
	i += 1	
	time.sleep(wait)


