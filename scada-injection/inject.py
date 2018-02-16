#!/usr/bin/python
"""
 Compare the HGR trackID with the outliers to obtain True and False count
"""
import csv
import subprocess
import os,sys
from os import path
import glob



datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets")

os.chdir(datasets)



"""
Find someway to reorganise raw file by takeing 1100 'normal' data points and putting at
the nead of a file and then adding shuffling and adding the rest.
For now using bash
"""   
#subprocess.call("/home/acox/code/scada-injection/./organiseDatasets.sh")

files=[]
for file in glob.glob('LE-logs/*.csv'):
    files.append(file)
    #print files

    outlier = file[23:][:-22]+"-forProcessing.csv"
    print outlier
    outlierTrackid = open('plots/outlierTrackid.csv','w')
    with open(outlier,'r')as out:
        for line in out:
            trackID = line.split('\t')
            o = line.split(' ')
            #print o[10]
            if "o" in o[12]:
                print >> outlierTrackid, trackID[0].lstrip() #contains trackID for all outlier labels.
                #print trackID[0].lstrip()
            """
            now to edit HGR files
            need seviery >3 HGR TrackID, Score padded to include 0 for missing trackID based on raw input
            severity <3 HGR, trackID, SCore padded to include 0 for missing trackID based on raw input
            HGR trackID all severity padded to include 0 for missing track ID based on outliers
            """

    HGRTrackid = open('plots/HGRTrackid.csv','w') #contains only the trackId
    HGRSeverity3 = open('plots/HGRSev3.csv', 'w') #contains all alerts >severity 3
    HGRSeverity1 = open ('plots/HGRSev1.csv', 'w') #coantins all alerts <severity 3
    lelogFile = file
    #print file
    with open(file, 'r') as le:
        for line in le:
            if "HGR" in line:
                t_ids = line.strip().split(',')
                 #print t_ids[4] # "track_ids":[27024]
                trackid = t_ids[4].split(':')
                score = t_ids[9].split(':')
                sev = t_ids[10].split(':')
                print >> HGRTrackid, str(trackid[1][1:-1])# remnoves [] from list
                if sev[1] >= 3:
                    print >> HGRSeverity3, str(trackid[1][1:-1]), score[1]
                else:
                    print >> HGRSeverity1, str(trackid[1][1:-1]), score[1]

    outlierTrackid.close()
    HGRTrackid.close()
    HGRSeverity3.close()
    HGRSeverity1.close()
    """
        Now compare the 2 above files - duplicates = TRUE POSITIVE
        if it's in HGRTrackid but not in outlierTrackid = FALSE POSITIVE
        if it's in outlierTrackid but not in HGRTrackid = TRUE NEGATIVE
    """

with open('plots/outlierTrackid.csv','r') as outlier: #read column from file into a list
    outl = [row[0] for row in csv.reader(outlier)]
    #print outl

with open('plots/HGRTrackid.csv','r') as leAnom:
    leAnom = [row[0] for row in csv.reader(leAnom)] 
#if in list2 but not list1 print 0 else if in both print value
#letid = [s if s in leAnom else '0' for s in outl] 

# list comprehension and matching if in 1 list and in another do xyz
match =  [x for x in leAnom if x in outl] 
falseNeg = [x for x in leAnom if x not in outl]
trueNeg = [x for x in outl if x not in leAnom]
print ("TRUE Positives: {}").format(len(match))
print ("FALSE Positive: {}").format(len(falseNeg))
print ("TRUE Negative: {}").format(len(trueNeg))

#compare HGRScore with HGR-for-plotting.csv to pad HGRScore so it includes 0's
test = open('plots/test.csv','w')
padded = open('plots/paddedHGRData.csv','w') # contains all HGR data from 1st trackid to last
#b =[]
cnt=1
with open('plots/HGRTrackid.csv','r') as leAnom:
    leAn = [row[0] for row in csv.reader(leAnom)] 
    for num in leAn:
        #print num
        b = int(num) - cnt
        print >> test, '0,'*b, num
        cnt = int(num) + 1

with open("plots/test.csv") as f:
    for line in f:
        line = line.rstrip()
        for word in line.split(','):
            print >> padded, word



os.remove("plots/test.csv")
#os.remove("plots/test2.csv")

subprocess.call("/home/acox/code/scada-injection/./addValueTopaddedHGR.sh")
#TODO: convert the above bash to python
    
#outlierTrackid.close()
#HGRTrackid.close()
#HGRSeverity3.close()
#HGRSeverity1.close()

        
            

