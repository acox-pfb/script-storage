#!/usr/bin/python

import csv
import os
import numpy as np
import pandas as pd
import glob
import fileinput
import shutil

# this script will work only for NAB data
# first inject the nab.csv data into the LE and copy that file back to $datasets
# under the $datasets/NAB directory ensure the original .csv is visible
# ensure $datasets/NAB/labels directory contains all label files (not in folders)
# then run this script to organize the data for injecting back into numenat for grading
# the 5 directories for copying into NAB/results/detector name are loacted in $datasets
# all the other data for plotting etc is under $datasets/NAB/tmp




datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets")
os.chdir(datasets)
LElogs=("learning_logs-LEX")

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


print "DONE WITH LABELS, WORKING ON LE FILES"
#get scores from learning_0.log files
files=[]
for f in glob.glob(LElogs+'/learning_0*.csv'):
    files.append(f)
    name = f
    filename = name[33:-4]
    dirName = 'z'+filename
    #print dirName, filename, name
    HGRall = open(dirName+'/HGR-ALL-'+filename, 'w')
    HGR1 = open(dirName+'/HGR-S1.csv', 'w') 
    HGR3 = open(dirName+'/HGR-S3.csv', 'w')
    writer = csv.writer(HGRall)
    writer.writerow(['trackID', 'anomaly_score']) # add as header
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
            writer.writerow([trackID[1:-1], Score])

            hgrSev = hgr[10]
            Sev = hgrSev.split(':')
            Severity = Sev[1]
            if Severity >= "3":
                writer3.writerow([trackID[1:-1], Score])
            else:
                writer1.writerow([trackID[1:-1], Score])
            #print >> HGR, trackID[1:-1], Score

    HGRall.close()
    HGR1.close()
    HGR3.close()
    
print "WORKING ON LEX FILES"
files=[]
for f in glob.glob(LElogs+'/learning_0*.csv'):
#for f in glob.glob(LElogs+'/learning_0.log-art_daily_jumpsdown.csv'):
    files.append(f)
    name = f
    filename = name[33:-4]
    dirName = 'z'+filename
    LEX = open(dirName+'/LEXScore.csv', 'w')
    writer = csv.writer(LEX, delimiter = ',')
    writer.writerow(['trackID', 'LEX_score']) # add as header
    for line in open(name):
        #print line
        if 'NAB,' in line:
            nab = line.split(',')        
            nabTrackId = nab[2]
            nabScore = nab[3][1:-1]
            #print nab[3]
            if nabScore == "3141593.0":
                #print nabScore
                nabScore = 0
                writer.writerow([nabTrackId,nabScore])
            else:
                nabScore = nabScore
                 #print >> LEX, nabTrackId, nabScore
                writer.writerow([nabTrackId,nabScore])
        
    LEX.close()        
      

print "DONE WITH FILES, MOVING ONTO  HGR FORMATTING"
dirFiles = []
for dName in glob.glob('z*'):
    #print d
    dirFiles.append(dName)
    #print dName
    os.chdir(datasets+'/'+dName)
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        #print f
        if f in glob.glob('tid*'):
            tid = f
            #print f
        elif f in glob.glob('labels*'):
                labels = f
                #print labels
        elif f in glob.glob('HGR-ALL*'):
                HGR = f
                #print HGR
        elif f in glob.glob('HGR-S1*'):
                HGRS1 = f
        elif f in glob.glob('HGR-S3*'):
                HGRS3 = f
   
     #create severity files for plotting only
    hg1 = pd.read_csv(tid)
    hg2 = pd.read_csv(HGRS1)
    hg3 = pd.read_csv(tid)
    hg4 = pd.read_csv(HGRS3)
    df1 = pd.read_csv(tid)
    df2 = pd.read_csv(HGR)

    data_merge = df1.merge(df2, how='left', on=None)
    data_merge.to_csv('merged.csv', index=None, header="trackId,timestamp,value,anomaly_score")
    
    data_merge = hg1.merge(hg2, how='left', on=None)
    data_merge.to_csv('mergedS1.csv', index=None, header="trackId,timestamp,value,anomaly_score")
    data_merge = hg3.merge(hg4, how='left', on=None)
    data_merge.to_csv('mergedS3.csv', index=None, header="trackId,timestamp,value,anomaly_score")


    # ADD 0 TO COLUMNS WHERE THERE IS NO HGR DATA - do the same for the severity plots
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

    finalS1 = open('Severity1.csv','w')

    with open('mergedS1.csv','r') as csvfileS1: #find empty rows and insert 0
        csvreader = csv.reader(csvfileS1)
        for row in csvreader:
            #print ','.join(row)
            if row[3] in (None, ""):
                print >> finalS1, ','.join(row), "0"
            else:
                print >> finalS1, ','.join(row)
    csvfileS1.close()
    finalS1.close() 

    finalS3 = open('Severity3.csv','w')

    with open('mergedS3.csv','r') as csvfileS3: #find empty rows and insert 0
        csvreader = csv.reader(csvfileS3)
        for row in csvreader:
            #print ','.join(row)
            if row[3] in (None, ""):
                print >> finalS3, ','.join(row), "0"
            else:
                print >> finalS3, ','.join(row)
    csvfileS3.close()
    finalS3.close() 



    LEXName = 'Results-wLEXScore'+dName[1:]+'.csv'
      #create timestamps, value, anomaly_score, label and LEX_score in final-LEX.csv
    df4 = pd.read_csv('final.csv')
    df5 = pd.read_csv('LEXScore.csv')
    merge = df5.merge(df4, how='left', on='trackID')
    merge.to_csv('Comparison-wLEXScore-andHGRScore.csv', index=None, header=True, columns=["timestamp","value","anomaly_score","LEX_score"])
    
    # now add labels column
    results = 'foundation_'+dName[1:]+'.csv'
    #print results
    #df1 = pd.read_csv('final.csv')
    #df2 = pd.read_csv('Comparison-wLEXScore-andHGRScore.csv')
    #df2 = pd.read_csv(labels) # this will put in teh HGR anomaly score
    #merge = df2.merge(df1, how='left', on='timestamp')
    #merge.to_csv(results, index=None, header=True, columns=["timestamp","value","anomaly_score","LEX_score","label"])

    LEX1 = pd.read_csv('Comparison-wLEXScore-andHGRScore.csv')
    label1 = pd.read_csv(labels)
    labelIntoLex = label1.merge(LEX1, how='left', on='timestamp')
    labelIntoLex.to_csv(LEXName, index=None, header=True, columns=["timestamp","value","anomaly_score","LEX_score","label"])
    LEXOnly = pd.read_csv(LEXName)
    LEXOnly.to_csv('resultstmp.csv', index=None, header=True, columns=["timestamp","value","LEX_score","label"])


    with open('resultstmp.csv', 'r') as read, open(results,'w') as write:
        reader = csv.reader(read)
        read.readline()
        writer = csv.writer(write, delimiter = ',')
        writer.writerow(["timestamp","value","anomaly_score","label"]) # add as header
        writer.writerows(reader)

    Sev1 = pd.read_csv('Severity1.csv')
    label1 = pd.read_csv(labels)
    labelIntoSev1 = label1.merge(Sev1, how='left', on='timestamp')
    labelIntoSev1.to_csv("Sev1.csv", index=None, header=True, columns=["timestamp","value","anomaly_score","label"])
    Sev3 = pd.read_csv('Severity3.csv')
    label3 = pd.read_csv(labels)
    labelIntoSev3 = label1.merge(Sev3, how='left', on='timestamp')
    labelIntoSev3.to_csv("Sev3.csv", index=None, header=True, columns=["timestamp","value","anomaly_score","label"])


    #if there is a HGR value make it the same as value
    df = pd.read_csv(results)
    df.to_csv("forplotting.csv", index=None, header=True, columns=["value", "anomaly_score", "label"])
    newval = 0
    with open("forplotting.csv", "r")as f, open('forplotting-spaces.csv','w') as write:
        writer = csv.writer(write, delimiter = ' ')
        f.readline()
        writer.writerow(["value", "anomaly_score", "label"]) # add as header
        for lines in f:
            val = lines.strip().split(',')
            if val[1] > "0.1":
                newval = val[0]
                #print >> write, val[0], newval, val[2]
                writer.writerow([val[0],newval,val[2]])
            else:
                val[1] = val[1]
                #print >> write, val[0], val[1], val[2]
                writer.writerow([val[0],val[1],val[2]])
    
    newvalS1 = 0
    with open("Sev1.csv", "r")as f, open('Plotting-Severity1.csv','w') as writeS1:
        writer = csv.writer(writeS1, delimiter = ',')
        f.readline()
        writer.writerow(["value", "anomaly_score", "label"]) # add as header
        for lines in f:
            val = lines.strip().split(',')
            if val[2] > "0.1":
                newvalS1 = val[1]
                writer.writerow([val[1],newvalS1,val[3]])
            else:
                val[1] = val[1]
                writer.writerow([val[1],val[2],val[3]])
    
    newvalS3 = 0
    with open("Sev3.csv", "r")as f, open('Plotting-Severity3.csv','w') as writeS3:
        writer = csv.writer(writeS3, delimiter = ',')
        f.readline()
        writer.writerow(["value", "anomaly_score", "label"]) # add as header
        for lines in f:
            val = lines.strip().split(',')
            if val[2] > "0.1":
                newvalS3 = val[1]
                writer.writerow([val[1],newvalS3,val[3]])
            else:
                val[1] = val[1]
                writer.writerow([val[1],val[2],val[3]])
    
    #with open('forplotting.csv', 'r') as read, open('forplotting-spaces.csv','w') as write:
    #    reader = csv.reader(read)
    #    writer = csv.writer(write, delimiter = ' ')
    #    writer.writerows(reader)

    os.remove('mergedS1.csv')
    os.remove('mergedS3.csv')
    os.remove('merged.csv')
    os.remove('final.csv')
    os.remove('HGR-S1.csv')
    os.remove('HGR-S3.csv')
    os.remove('Comparison-wLEXScore-andHGRScore.csv')
    os.remove('forplotting.csv')
    os.remove('Sev1.csv')
    os.remove('Severity1.csv')
    os.remove('Sev3.csv')
    os.remove('Severity3.csv')
    os.remove('LEXScore.csv')
print " Organising Files Now"
os.chdir(datasets)

if os.path.exists('LEX-NABResults-Folders'):
    shutil.rmtree('LEX-NABResults-Folders')
os.mkdir("LEX-NABResults-Folders")
if os.path.exists('LEX-NABResults-Folders/artificialNoAnomaly'):
    shutil.rmtree('LEX-NABResults-Folders/artificialNoAnomaly')
os.mkdir("LEX-NABResults-Folders/artificialNoAnomaly")
for f in glob.glob('zart_daily_no_*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialNoAnomaly')
for f in glob.glob('zart_daily_perf*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialNoAnomaly')
for f in glob.glob('zart_daily_smal*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialNoAnomaly')
for f in glob.glob('zart_flatline*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialNoAnomaly')
for f in glob.glob('zart_noisy*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialNoAnomaly')
if os.path.exists('LEX-NABResults-Folders/artificialWithAnomaly'):
    shutil.rmtree('LEX-NABResults-Folders/artificialWithAnomaly')
os.mkdir("LEX-NABResults-Folders/artificialWithAnomaly")
for f in glob.glob('zart_daily_flat*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsd*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsu*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
for f in glob.glob('zart_daily_noj*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
for f in glob.glob('zart_increase*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
for f in glob.glob('zart_load*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/artificialWithAnomaly')
if os.path.exists('LEX-NABResults-Folders/realAdExchange'):
    shutil.rmtree('LEX-NABResults-Folders/realAdExchange')
os.mkdir("LEX-NABResults-Folders/realAdExchange")
for f in glob.glob('zexchange*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realAdExchange')
if os.path.exists('LEX-NABResults-Folders/realAWSCloudwatch'):
    shutil.rmtree('LEX-NABResults-Folders/realAWSCloudwatch')
os.mkdir("LEX-NABResults-Folders/realAWSCloudwatch")
for f in glob.glob('zec2_c*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('zec2_d*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('zec2_n*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('zelb*/foun*'):
    shutil.move(f,'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('zgro*/foun*'):
    shutil.move(f,'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('ziio*/foun*'):
    shutil.move(f,'LEX-NABResults-Folders/realAWSCloudwatch')
for f in glob.glob('zrds*/foun*'):
    shutil.move(f,'LEX-NABResults-Folders/realAWSCloudwatch')
if os.path.exists('LEX-NABResults-Folders/realKnownCause'):
    shutil.rmtree('LEX-NABResults-Folders/realKnownCause')
os.mkdir("LEX-NABResults-Folders/realKnownCause")
for f in glob.glob('zambient*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
for f in glob.glob('zcpu_u*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
for f in glob.glob('zec2_r*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
for f in glob.glob('zmachine*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
for f in glob.glob('znyc*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
for f in glob.glob('zrogue*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realKnownCause')
if os.path.exists('LEX-NABResults-Folders/realTraffic'):
    shutil.rmtree('LEX-NABResults-Folders/realTraffic')
os.mkdir("LEX-NABResults-Folders/realTraffic")
for f in glob.glob('zocc*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realTraffic')
for f in glob.glob('zspeed*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realTraffic')
for f in glob.glob('zTravel*/foun*'):
    shutil.move(f, 'LEX-NABResults-Folders/realTraffic')
if os.path.exists('LEX-NABResults-Folders/realTweets'):
    shutil.rmtree('LEX-NABResults-Folders/realTweets')
os.mkdir("LEX-NABResults-Folders/realTweets")
for f in glob.glob('zTwitt*/foun*'):
    shutil.move(f,'LEX-NABResults-Folders/realTweets')
#move all zdirectories into tmp
if os.path.exists('NAB/tmpFiles'):
    shutil.rmtree('NAB/tmpFiles')
os.mkdir('NAB/tmpFiles/')
for f in glob.glob('z*'):
    dst = "NAB/tmpFiles/"
    shutil.move(f,dst)



