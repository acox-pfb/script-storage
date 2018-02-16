#!/usr/bin/python

import csv
import os
import numpy as np
import pandas as pd
import glob
import fileinput
import shutil

# this script will work only for NAB data
# first inject the nab.csv data into the LE and copy that file back to:
# /home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets
# under the NAB directory ensure the original .csv is visible
# ensure NAB/labels directory contains all label files (not in folders)
# then run this script to organize the data for injecting back into numenat for grading




datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets")
os.chdir(datasets)

# add a new column to art.csv as trackID
raw = []
dirName=[]
for x in glob.glob('NAB/*.csv'):
    raw.append(x)
    name = x[4:]
    dirName = 'z'+name[:-4]
    if os.path.exists(dirName):
        shutil.rmtree(dirName)
    os.mkdir(dirName)
       
    #print name, dirName
    shutil.copyfile(x, name)
       
    df = pd.read_csv(name)
    df.insert(0,'trackID',df.index+1)
    df.to_csv('tid'+name, index=False)
    shutil.move('tid'+name, dirName)

# get labels from datasets/NAB
labels = []
for x in glob.glob('NAB/labels/numenta*.csv'):
    labels.append(x)
    name = x
    labelName = name[11:-4]
    dirName = 'z'+labelName[8:]
    #print labelName, dirName
    #read and extrack labels into label file
    cols = ['timestamp', 'label']
    pd.read_csv(name,usecols=cols).to_csv('labels'+labelName, index=False)
    shutil.move('labels'+labelName, dirName)


#print "DONE WITH LABELS"
#get scores from learning_0.log files
files=[]
for f in glob.glob('learning_0*.csv'):
    files.append(f)
    name = f
    filename = name[15:-4]
    dirName = 'z'+filename
    #print dirName, filename, name
    HGR1 = open(dirName+'/HGR-Sev1-'+filename, 'w') 
    HGR3 = open(dirName+'/HGR-Sev3-'+filename, 'w')
    writer1 = csv.writer(HGR1)
    writer1.writerow(['trackID', 'anomaly_score']) # add as header
    writer3 = csv.writer(HGR3)
    writer3.writerow(['trackID', 'anomaly_score']) # add as header
    #print files[0]

    for line in open(name):
        #print line
        if 'HGR' in line:
            #print line
            hgr = line.split(',')
            hgrTID=hgr[4]
            tID = hgrTID.split(':')
            trackID = tID[1]

            hgrSc = hgr[9]
            Sc = hgrSc.split(':')
            Score = Sc[1]


            hgrSev = hgr[10]
            Sev = hgrSev.split(':')
            Severity = Sev[1]
            if Severity >= "3":
                writer3.writerow([trackID[1:-1], Score])
            else:
                writer1.writerow([trackID[1:-1], Score])
            #print >> HGR, trackID[1:-1], Score
            
    
    #shutil.move(HGR, dirName)
    

    HGR1.close()
    HGR3.close()

#print "DONE WITH FILE"
dirFiles = []
for dName in glob.glob('z*'):
    #print d
    dirFiles.append(dName)
    print dName
    os.chdir(datasets+'/'+dName)
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        #print f
        if f in glob.glob('tid*'):
            tid = f
            print f
        elif f in glob.glob('labels*'):
                labels = f
                print labels
        elif f in glob.glob('HGR*'):
                HGR = f
                print HGR
    #labels = dirListing[1]
    #HGR = dirListing[2]
    #print tid

    #print "STUCK HERE??"
    df1 = pd.read_csv(tid)
    df2 = pd.read_csv(HGR)

    data_merge = df1.merge(df2, how='left', on=None)
    data_merge.to_csv('merged.csv', index=None, header="trackId,timestamp,value,anomaly_score")
    
    # ADD 0 TO COLUMNS WHERE THERE IS NO HGR DATA
    final = open('final.csv','w')

    with open('merged.csv','r') as csvfile: #find empty rows and insert 0
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            #print ','.join(row)
            if row[3] in (None, ""):
                print >> final, ','.join(row), "0"
            else:
                print >> final, ','.join(row)
    csvfile.close()
    final.close() 
    
    # now add labels column
    results = 'foundation_'+dName[1:]+'.csv'
    #print results
    
    df1 = pd.read_csv('final.csv')
    df2 = pd.read_csv(labels)
    merge = df2.merge(df1, how='left', on='timestamp')
    merge.to_csv(results, index=None, header=True, columns=["timestamp","value","anomaly_score","label"])

    df = pd.read_csv(results)
    df.to_csv("forplotting.csv", index=None, header=True, columns=["value", "anomaly_score", "label"])
    newval = 0
    with open("forplotting.csv", "r")as f, open('forplotting-spaces.csv','w') as write:
        for lines in f:
            val = lines.strip().split(',')
            if val[1] > "0.1":
                newval = val[0]
                print >> write, val[0], newval, val[2]
            else:
                val[1] = val[1]
                print >> write, val[0], val[1], val[2]

    #with open('forplotting.csv', 'r') as read, open('forplotting-spaces.csv','w') as write:
    #    reader = csv.reader(read)
    #    writer = csv.writer(write, delimiter = ' ')
    #    writer.writerows(reader)

    os.remove('merged.csv')
    os.remove('final.csv')

os.chdir(datasets)
os.mkdir("artificialNoAnomaly")
for f in glob.glob('zart_daily_no_*/foun*'):
    shutil.move(f, 'artificialNoAnomaly')
for f in glob.glob('zart_daily_perf*/foun*'):
    shutil.move(f, 'artificialNoAnomaly')
for f in glob.glob('zart_daily_smal*/foun*'):
    shutil.move(f, 'artificialNoAnomaly')
for f in glob.glob('zart_flatline*/foun*'):
    shutil.move(f, 'artificialNoAnomaly')
for f in glob.glob('zart_noisy*/foun*'):
    shutil.move(f, 'artificialNoAnomaly')
os.mkdir("artificialWithAnomaly")
for f in glob.glob('zart_daily_flat*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsd*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsu*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
for f in glob.glob('zart_daily_noj*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
for f in glob.glob('zart_increase*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
for f in glob.glob('zart_load*/foun*'):
    shutil.move(f, 'artificialWithAnomaly')
os.mkdir("realAdExchange")
for f in glob.glob('zexchange*/foun*'):
    shutil.move(f, 'realAdExchange')
os.mkdir("realAWSCloudwatch")
for f in glob.glob('zec2_c*/foun*'):
    shutil.move(f, 'realAWSCloudwatch')
for f in glob.glob('zec2_d*/foun*'):
    shutil.move(f, 'realAWSCloudwatch')
for f in glob.glob('zec2_n*/foun*'):
    shutil.move(f, 'realAWSCloudwatch')
for f in glob.glob('zelb*/foun*'):
    shutil.move(f,'realAWSCloudwatch')
for f in glob.glob('zgro*/foun*'):
    shutil.move(f,'realAWSCloudwatch')
for f in glob.glob('ziio*/foun*'):
    shutil.move(f,'realAWSCloudwatch')
for f in glob.glob('zrds*/foun*'):
    shutil.move(f,'realAWSCloudwatch')
os.mkdir("realKnownCause")
for f in glob.glob('zambient*/foun*'):
    shutil.move(f, 'realKnownCause')
for f in glob.glob('zcpu_u*/foun*'):
    shutil.move(f, 'realKnownCause')
for f in glob.glob('zec2_r*/foun*'):
    shutil.move(f, 'realKnownCause')
for f in glob.glob('zmachine*/foun*'):
    shutil.move(f, 'realKnownCause')
for f in glob.glob('znyc*/foun*'):
    shutil.move(f, 'realKnownCause')
for f in glob.glob('zrogue*/rofoung*'):
    shutil.move(f, 'realKnownCause')
os.mkdir("realTraffic")
for f in glob.glob('zocc*/foun*'):
    shutil.move(f, 'realTraffic')
for f in glob.glob('zspeed*/foun*'):
    shutil.move(f, 'realTraffic')
for f in glob.glob('zTravel*/foun*'):
    shutil.move(f, 'realTraffic')
os.mkdir("realTweets")
for f in glob.glob('zTwitt*/foun*'):
    shutil.move(f,'realTweets')
#move all zdirectories into tmp
if os.path.exists(datasets+'/NAB/tmp'):
    shutil.rmtree(datasets+'/NAB/tmp')
os.mkdir(datasets+'/NAB/tmp')
for f in glob.glob('z*'):
    shutil.move(f,datasets+'/NAB/tmp')

 

