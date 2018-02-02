#!/usr/bin/python3
import time
import os
import psutil
cmd="/opt/omniai/bin/scadactl -c push "
video_sensor_id = "18"
learning_sensor_id = "19"
data_sensor_id = "20"
video_sensor="foundation-video"
data_sensor="foundation-scada"
learning_sensor="foundation-learning"
cpu_resource='cpu_percent'
memory_resource='memory_percent'


i=1
clock = 5
wait = 10



def build_cmd(sensor_id,sensor_name):
	def pid(process_name):
		for proc in psutil.process_iter():
			pinfo = proc.as_dict(attrs=['pid', 'name'])
			p_name = pinfo['name']
			p_pid = pinfo['pid']
			if process_name == p_name:
				return p_pid
		return -999

	process_status = pid(sensor_name)
	if process_status != -999:
		p = psutil.Process(pid(sensor_name))
		epoch_time = str(int(time.time()))+"000000"
		scadactl_cmd1 = cmd + sensor_id + " " + str(p.cpu_percent(interval=1)) + " " +  epoch_time
		return scadactl_cmd1
	else:
		return -9999
while i <= clock:

	cmd1=build_cmd(data_sensor_id,data_sensor)
	if cmd1 != -9999:
		os.system(cmd1)
	cmd2=build_cmd(learning_sensor_id,learning_sensor)
	if cmd2 != -9999:
		os.system(cmd2)
	cmd3=build_cmd(video_sensor_id,video_sensor)
	if cmd3 != -9999:
		os.system(cmd3)
	i += 1
	time.sleep(wait)

exit(0)
