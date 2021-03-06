#!/usr/bin/python

#when inputting sensor count keep it to groups of 10, crashes otherwise
# 31 August 2016. ACOX edited script to it will only run locally now.

import requests
#from requests.auth import HTTPBasicAuth
import random
import time
import json
import itertools
import argparse
import subprocess

username='admin'
password='adminadmin'
host='localhost'

#sCount=raw_input("Enter number of sensors to create:")
#@todo parmaterize all of these
#numGroups=10
#baseGroupName='scalabilityVideoGroup'

#numSensors=int(sCount) #convert from sting input to int.
#numSensors=args.num-sensors #convert from sting input to int.
basePrimitiveSensorName='VideoSensor'

tarFPS=8
clipLength=5
updateInterval=60000
alertingOdds=1000
txtColor="FFFFFF"
alertSuppressionPeriod=0
#when creating sensors it will iterate through this list for the url and create a new url for each sensor
#vidurl=["file://home/acox/HSCO-DowntownStreet-15minDay-AbandonedObject.mp4"]
#vidurl=["rtsp://aisight:TheAIDoctors@192.168.26.214:5554/pkway"] #low vidgen activity
#vidurl=["file://home/aisight/Videos/pkwy_day-8fps_1hr.avi"]
#vidurl=["file://home/aisight/Videos/rooftop_4hr.avi"] #low unstable video activity
#vidurl=["file://home/aisight/videos/test_49_twice.mp4"] #low vidgen activity
#vidurl=["file://home/aisight/videos/test51_extended.mp4"] #medium vidgen activity
#vidurl=["file://home/aisight/videos/test42_extended.mp4"] #high vidgen activity
vidurl="rtsp://192.168.26.214:5554/HotelCircle" #low activity
#vidurl="file://home/aisight/Videos/zHotelCircle.mp4"
#vidurl=["z610Feed.mp4"] #medium activity
#vidurl="file://home/aisight/Videos/z610Feed.mp4"
#vidurl=["610Offramp.mp4"] #high activity
#vidurl="file://home/aisight/Videos/z610OffRamp.mp4"
postClipLen=0
trajClip=False
thermCam=False
imgStab=False
defWidth=352
defHeight=288

#groupIds=dict()
sensorIds=dict()


#def createVideoGroup(groupName):
#  payload = {'name' : groupName}
#  url = "http://{}:8080/api/sensor-groups".format(host)
#  headers= {'Content-Type' : 'application/json',
#              'Accept' : 'application/json'}

#  jsonPayload = json.dumps(payload)
#  r = requests.post(url, headers=headers, data=jsonPayload, auth=(username, password))

#  print "response status code = {}".format(r.status_code)
#  if r.status_code != requests.codes.ok:
#	r.raise_for_status()
#  else:
#	responseSensor = r.json()
#	return responseSensor['id']

#def createVideoSensor(name, group, vid_index):
def createVideoSensor(name, vid_index):
    sensorType= { 'id' : 1}
    analysisServer= { 'id' : 2}
#    sensorGroups= { 'sensorGroup' : [{'id': groupIds[group]}] }
    payload = {
        'name' : name,
        'targetFPS' : tarFPS,
        'url' : vidurl[vid_index],
        'alertClipLength' : clipLength,
        #               'updateInterval' : updateInterval,
        'alertingOdds' : alertingOdds,
        'alertClipTextColor' : txtColor,
        'postAlertClipLength' : postClipLen,
        'fullTrajectoryClip' : trajClip,
        'thermalCamera' : thermCam,
	'imageStabilization' : imgStab,
	'targetWidth' : defWidth,
	'targetHeight' : defHeight,
        'sensorType': sensorType,
#        'sensorGroups' : sensorGroups,
        'analysisServer' : analysisServer,
        'alertSuppressionPeriod' : alertSuppressionPeriod 
    }
    url = "http://{}:8080/api/sensors".format(host)
    headers= {'Content-Type' : 'application/json',
              'Accept' : 'application/json'}
    print url
    jsonPayload = json.dumps(payload)	
    r = requests.post(url, headers=headers, data=jsonPayload, auth=(username, password))
    print "response status code = {}".format(r.status_code)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    else:
        responseSensor = r.json()
    return responseSensor['id']
"""
def createVideoSensor(name, vid_index):
	print "name = {}".format(name)
	print "vid_index = {}".format(vid_index)
	print "url = {}".format(vidurl)
	x = subprocess.call(["/opt/graydient/bin/videoctl", "-c", "create", name, str(vid_index), str(vidurl)])	
	print "x={}".format(x)
"""
#main script entry
if __name__ == "__main__": #anything within this function can not be ran/accessed remotely
	parser = argparse.ArgumentParser(description='Pass in sensor number to create, default is now 10')
	parser.add_argument('-n', '--numSensors', type=int, required=False, default=5, help='Number of sensors to start')
	args = parser.parse_args()
	

#	for group in range(1, numGroups+1):
#		groupName="{}-{:02d}".format(baseGroupName, group)
#		print "groupName={}".format(groupName)
#		groupId = createVideoGroup(groupName)
#		groupIds[group]=groupId


	for index in range(1, args.numSensors+1):
#		group = ((index - 1) // (args.numSensors // numGroups)) + 1
		name="{}-{:05d}".format(basePrimitiveSensorName, index)
    
		vid_index = (index-1) % len(vidurl)
		#print vid_index
#		newSensorId=createVideoSensor(name,group, vid_index)
 		newSensorId=createVideoSensor(name, vid_index)  
		print "newSensorId = {}".format(vid_index) 
#		sensorIds[vid_index]=newSensorId
    
		sensId = open("zsensorId.txt","w")
		print >> sensId, "created new primitive sensor with id= {}".format(vid_index)
		sensId.close()

