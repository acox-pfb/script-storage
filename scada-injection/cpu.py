#!/usr/bin/python3
import time
import os
import psutil


cmd="/opt/omniai/bin/scadactl -c push "


 
cpu = "1136" 
i=1
clock = 500000
wait = 10

while i <= clock:
	epoch_time = str(int(time.time()))+"000000"
	current_cpu = psutil.cpu_percent()
	scadactl_cmd1 = cmd + cpu + " " + str(current_cpu) + " " +  epoch_time
	os.system(scadactl_cmd1)
	i += 1	
	time.sleep(wait)

exit(0)
