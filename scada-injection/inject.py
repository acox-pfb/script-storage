#!/usr/bin/python
"""
 Compare the HGR trackID with the outliers to obtain True and False count
"""
import csv
import os,sys


le_logs=("/home/omniai/Features/AllFeatures/learning_logs")

os.chdir(le_logs)
HGRtid = open('HGR-tid.csv','w')
outtid = open('outtid.csv','w')
with open('learning_0.log-shuttle-shuffled-data.csv', 'r') as le:
    for line  in le:
        if "HGR" in line:
            t_ids = line.strip().split(',')
            #print t_ids[4] # "track_ids":[27024]
            tid = t_ids[4].split(':')
            print >> HGRtid, str(tid[1][1:-1]) # remnoves [] from list

with open('shuttle-shuffled-outlier-trackIDs','r') as out:
        for line in out:
                tid = line.split(':')
                print >> outtid, tid[0]

HGRtid.close()
outtid.close()

"""
Now compare the 2 above files - duplicates = TRUE POSITIVE
if it's in HGRtid but not in outtid = FALSE POSITIVE
if it's in outtid but not in HGRtid = TRUE NEGATIVE
"""

with open('HGR-tid.csv','r') as le_tid:
    letid = [row[0] for row in csv.reader(le_tid)]
    #print letid
    
with open('outtid.csv','r') as outlier:
    outl = [row[0] for row in csv.reader(outlier)]
    #print outl

#number_of_alerts = len(letid)
#number_of_true_alerts = len(outl)
#print number_of_alerts, number_of_true_alerts

match =  [x for x in letid if x in outl]
falseNeg = [x for x in letid if x not in outl]
trueNeg = [x for x in outl if x not in letid]
print ("TRUE Positives: {}").format(len(match))
print ("FALSE Positive: {}").format(len(falseNeg))
print ("TRUE Negative: {}").format(len(trueNeg))

    

        
            

