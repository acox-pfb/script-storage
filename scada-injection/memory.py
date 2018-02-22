#!/usr/bin/python3
import time
import os
import psutil


cmd="/opt/omniai/bin/scadactl -c push "


 
ram = "1142" 
i=1
clock = 500000
wait = 10

while i <= clock:
	epoch_time = str(int(time.time()))+"000000"
	virtual_ram = psutil.virtual_memory()
	scadactl_cmd1 = cmd + ram + " " + str(virtual_ram.percent) + " " +  epoch_time
	os.system(scadactl_cmd1)
	print(scadactl_cmd1)
	i += 1	
	time.sleep(wait)

exit(0)
