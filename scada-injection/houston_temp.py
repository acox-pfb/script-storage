#!/usr/bin/python3
import time
import subprocess
import pyowm

cmd="/opt/omniai/bin/scadactl -c push "
owm = pyowm.OWM('ee47fb921532fab91cda7997463ce28a')

observation = owm.weather_at_zip_code('77084','US')
w = observation.get_weather()
#w.get_wind()                  # {'speed': 4.6, 'deg': 330}
#w.get_humidity()              # 87
current_temp_77084 = (w.get_temperature('fahrenheit')['temp'])  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
#print(current_temp_77084)

 
temp_77084 = "5" 
i=1
clock = 5
wait = 10

while i <= clock:
	epoch_time = str(int(time.time()))+"000000"
	scadactl_cmd1 = cmd + temp_77084 + " " + str(current_temp_77084) + " " +  epoch_time
	subprocess.Popen(scadactl_cmd1,shell=True)
	i += 1	
	time.sleep(wait)

