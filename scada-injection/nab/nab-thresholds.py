#!/usr/bin/python

import csv
import os
import json
from pprint import pprint
import time
import subprocess

"""
    open ~/NAB/config/thresholds.json
    edit the threshold values for foundation:
        "foundation": {
            "reward_low_FN_rate": {
                "score": -4214.261823974466,
                "threshold": 0.999
            },
            "reward_low_FP_rate": {
                "score": -8446.89691408145,
                "threshold": 0.999
            },
            "standard": {
                "score": -4191.261823974466,
                "threshold": 0.999
            }
    Run: python run.py -d foundation --score --normalize from ~/NAB/
start with threshold vale at 0.9000 and increase 0.2 up till 1.000
""" 

thresholdValue = 0.9000
maxThreshold = 1.0
config = ("/home/acox/NAB/")
final_results = ("/home/acox/NAB/results")
os.chdir(config)
os.remove('Foundation-threshold-Results.csv')

#with open('thresholds.json','r') as jsonFile:
#    data = json.load(jsonFile)
#    pprint(data)
while (thresholdValue <= maxThreshold):
    data = json.load(open('config/thresholds.json'))
    tmpFN = data["foundation"]["reward_low_FN_rate"]["threshold"]
    tmpFP = data["foundation"]["reward_low_FP_rate"]["threshold"]
    tmpStandard = data["foundation"]["standard"]["threshold"]

    data["foundation"]["reward_low_FN_rate"]["threshold"] = thresholdValue
    data["foundation"]["reward_low_FP_rate"]["threshold"] = thresholdValue
    data["foundation"]["standard"]["threshold"] = thresholdValue
    with open('config/thresholds.json', 'w') as jsonFile:
        json.dump(data, jsonFile, sort_keys=True, indent=4, separators=(',', ':'))
        #pprint(data["foundation"])

    jsonFile.close()
   
    cmd = "python run.py -d foundation --skipConfirmation --score --normalize"
    os.system(cmd)
    #p=subprocess.Popen(cmd.split(), stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
    

    time.sleep(60) # set to 60secs. without --optimize shoudl take 50secs-ish

    results = json.load(open(final_results+'/final_results.json'))
    pprint(results["foundation"])

    with open('Foundation-threshold-Results.csv', 'a') as outputFile:
        print >> outputFile, "\n\n\tThreshold Value: {}".format(thresholdValue)
        json.dump(results["foundation"], outputFile, sort_keys=True, indent=4, separators=(',', ':'))

    outputFile.close()
    thresholdValue += 0.0002 # set to 0.002