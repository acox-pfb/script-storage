#!/usr/bin/python

import csv
import os
import numpy as np
import pandas as pd
import glob
import fileinput
import shutil
import argparse
import random
import time
from datetime import datetime, timedelta
#import plot

# for NAB data clone respository to ~/NAB
# for harvard data download to ~/harvard/
# for all others downlaod to ~/mlData

# if using NAB data then run with -l flag to pull the data for injection and sort out labels
# inject the nab.csv data that now resides in $timeSeries
# NAB labels are copied into $timeSeries - labels...csv
# tid..csv files are NAB data with trackID column - needed for processing
# Processing flag -p will edit the LE files for HGR data, it will put it in the format:
#  timestamp, value, anomaly_score, label 
#  and it will then sort it back into the original folders under $datasets
# if running through numenta:
# copy the original folders from $datasets into NAB/results/detector name are loacted in $datasets
# Plotting is also in the original folders under $datasets 


datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets")
nab_dataset=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets/NAB/")
harvard_dataset=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets/harvard/")
harvard = ("/home/acox/harvard/")
nab=("/home/acox/NAB/data/")
label=("/home/acox/NAB/results/numenta/")
os.chdir(nab_dataset)
LElogs=("learning_logs-LEX")

training="200"

def nab_data():
    if args.nab_data:
        print "Copy NAB files from NAB repository to {} ready for injecting".format(nab_dataset)
# add a new column to art...csv as trackID
        walk = []
        raw = []    
        #dirName=[]
        for path, subdirs, files in os.walk(nab):
            #print nab
            for name in files:
                walk.append(os.path.join(path, name))
                #print walk
        files = [s for s in walk if ".csv" in s]
        #print files
        for x in files:
            raw.append(x)
            name = x.split('/')
            fileName = name[6]
            dirName = 'z'+fileName
            #print dirName
            if os.path.exists(dirName):
                shutil.rmtree(dirName)
            os.mkdir(dirName)
       
            #print fileName, dirName

            shutil.copyfile(x, fileName)
            #print x, fileName, dirName
       
            df = pd.read_csv(fileName)
            df.insert(0,'trackID',df.index+1)
            df.to_csv('tid'+fileName, index=False)
            shutil.move('tid'+fileName, dirName)

        # get labels from datasets/NAB
        labels = []
        raw = []
        for path, subdirs, files in os.walk(label):
            #print files
            for name in files:
                labels.append(os.path.join(path, name))
                #print labels
        files = [s for s in labels if ".csv" in s]

        for x in files[3:]:
            raw.append(x)
            name = x.split('/')
            resultsLabelName = name[7]
            labelName = resultsLabelName.split('_')
            #print labelName
            dname = 'z'+"_".join(labelName[1:])
            #print dname
            lname = "l_"+"_".join(labelName[1:])
            #print "_".join(labelName[1:]), dirName
            shutil.copyfile(x, lname)
            #print x, lname, dirName
            cols = ['timestamp', 'label']
            pd.read_csv(lname, usecols=cols).to_csv('labels'+"_".join(labelName[1:]), index=False)
            #print "labels"+"_".join(labelName[1:]), dname
            shutil.move("labels"+"_".join(labelName[1:]), dname)

        for filename in glob.glob("l_*.csv"):
            os.remove(filename)
        
        
    else:
        exit(0)

def harvard_data():
    #only use datasets with <32 features
    #shuffle data and then double it
    #in LE set SCADA_D2H_INTERVAL= to length oforiginal file

    #files = []
      
    if args.harvard_data:
        print "Editing harvard data and copying to {} for injecting".format(harvard_dataset)
        os.chdir(harvard) # only copy files where columns < 32
       # print files
        for f in glob.glob("*"):
            #print f
            files = open(f,"r")
            reader = csv.reader(files, delimiter="\t")
            ncol=len(next(reader))
            if ncol <= 32:
                dirName = 'z'+f[:-7]
                #print f, dirName
                if os.path.exists(harvard_dataset+'/'+dirName):
                    shutil.rmtree(harvard_dataset+'/'+dirName)
                os.mkdir(harvard_dataset+'/'+dirName)
                shutil.copyfile(f, harvard_dataset+dirName+'/'+f)
            else:
                print "ERRR"
        
        # all valid files are now in harvard_dataset directories
        # now get length of files, shuffle them and double them
        walk = []
        raw = []
        shuff=[] # shuffle    
        #dirName=[]
        os.chdir(harvard_dataset)
        for path, subdirs, files in os.walk("."):
            #print nab
            for name in files:
                walk.append(os.path.join(path, name))
                #print walk
        subfiles = [s for s in walk if ".tab" in s]
        #print subfiles
        if os.path.exists('harvard_numLines.csv'):
                os.remove('harvard_numLines.csv')
        for f in subfiles:
            raw.append(f)
            with open(f) as fin, open('harvard_numLines.csv', 'a') as numLines:
                #writer = csv.writer(head, delimiter = ' ')
                num_lines = sum(1 for line in open(f))
                print >> numLines, f, num_lines # set SCADA_D2H_INTERVAL in config to this value
                numLines.close()

        #now shuffle files
                li = fin.readlines()
                random.shuffle(li)
                fid = open(f[:-7]+'-shuffled.csv', 'w')
                fid.writelines(li)
                fid.close()
        #Double length of files
                shutil.copyfile(f[:-7]+'-shuffled.csv', f[:-7]+'-copied.csv')
                filenames = [f[:-7]+'-shuffled.csv', f[:-7]+'-copied.csv']
                #print filenames
                with open(f[:-7]+'-doubled.csv', 'w') as fout:
                    fin = fileinput.input(filenames)
                    for line in fin:
                        fout.write(line)
                    fin.close()
                    os.remove(f[:-7]+'-shuffled.csv')
                    os.remove(f[:-7]+'-copied.csv')
        #Add timeseries and trackID for easy plotting
            startdate = datetime.strptime ("2018-01-01 00:00:01", "%Y-%m-%d %H:%M:%S")
            #print startdate
            with open(f[:-7]+'-doubled.csv', 'r') as timeIn, open(f[:-7]+'-timeseries.csv', 'w') as timeOut:
                writer = csv.writer(timeOut, delimiter="\t")
                for x in timeIn:
                   startdate += timedelta(seconds=1)
                   print >> timeOut, startdate
            
            df1 = pd.read_csv(f[:-7]+'-doubled.csv', sep='\t')
            df2 = pd.read_csv(f[:-7]+'-timeseries.csv', usecols=[0])

            x = df2.join(df1)
            #x = pd.merge(df1, df2, left_on='col1', right_index=True)
            x.to_csv(f[:-7]+'-doubleTimeseries.csv', index=None) 

            os.remove(f[:-7]+'-doubled.csv')
            os.remove(f[:-7]+'-timeseries.csv')
            with open(f[:-7]+'-doubleTimeseries.csv', 'r') as openfile, open(f[:-7]+'-trackIDTimeseries.csv','w') as outfile:
                for j, line in enumerate(openfile):
                    outfile.write('%d,%s' %(j+1, line))
            # now create a new file from double timeseries and remove the label column for injecting
            with open(f[:-7]+'-doubleTimeseries.csv','r') as tid, open(f[:-7]+'-forInjecting.csv', 'w') as inject:
                writer = csv.writer(inject)
                for row in csv.reader(tid):
                    writer.writerow(row[:-1])


    else:
        exit(0)

def timeseries():
    if args.timeseries:
        print "files have timeseries but no labels"
    else:
        exit(0)

def processing():
    if args.process_only:
        print "processing"
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


            # now add labels column
            results = 'foundation_'+dName[1:]+'.csv'
            #print results
            
            df1 = pd.read_csv('final.csv')
            df2 = pd.read_csv(labels)
            merge = df2.merge(df1, how='left', on='timestamp')
            merge.to_csv(results, index=None, header=True, columns=["timestamp","value","anomaly_score","label"])

            Sev1 = pd.read_csv('Severity1.csv')
            label1 = pd.read_csv(labels)
            labelIntoSev1 = label1.merge(Sev1, how='left', on='timestamp')
            labelIntoSev1.to_csv("Sev1.csv", index=None, header=True, columns=["timestamp","value","anomaly_score","label"])
            Sev3 = pd.read_csv('Severity3.csv')
            label3 = pd.read_csv(labels)
            labelIntoSev3 = label1.merge(Sev3, how='left', on='timestamp')
            labelIntoSev3.to_csv("Sev3.csv", index=None, header=True, columns=["timestamp","value","anomaly_score","label"])


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
        os.remove('forplotting.csv')
        os.remove('Sev1.csv')
        os.remove('Severity1.csv')
        os.remove('Sev3.csv')
        os.remove('Severity3.csv')

        print " Organising Files Now"
        os.chdir(datasets)

        if os.path.exists('artificialNoAnomaly'):
            shutil.rmtree('artificialNoAnomaly')
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
        if os.path.exists('artificialWithAnomaly'):
            shutil.rmtree('artificialWithAnomaly')
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
        if os.path.exists('realAdExchange'):
            shutil.rmtree('realAdExchange')
        os.mkdir("realAdExchange")
        for f in glob.glob('zexchange*/foun*'):
            shutil.move(f, 'realAdExchange')
        if os.path.exists('realAWSCloudwatch'):
            shutil.rmtree('realAWSCloudwatch')
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
        if os.path.exists('realKnownCause'):
            shutil.rmtree('realKnownCause')
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
        for f in glob.glob('zrogue*/foun    *'):
            shutil.move(f, 'realKnownCause')
        if os.path.exists('realTraffic'):
            shutil.rmtree('realTraffic')
        os.mkdir("realTraffic")
        for f in glob.glob('zocc*/foun*'):
            shutil.move(f, 'realTraffic')
        for f in glob.glob('zspeed*/foun*'):
            shutil.move(f, 'realTraffic')
        for f in glob.glob('zTravel*/foun*'):
            shutil.move(f, 'realTraffic')
        if os.path.exists('realTweets'):
            shutil.rmtree('realTweets')
        os.mkdir("realTweets")
        for f in glob.glob('zTwitt*/foun*'):
            shutil.move(f,'realTweets')
        #move all zdirectories into tmp
        if os.path.exists('NAB/tmpFiles'):
            shutil.rmtree('NAB/tmpFiles')
        os.mkdir('NAB/tmpFiles/')
        for f in glob.glob('z*'):
            dst = "NAB/tmpFiles/"
            shutil.move(f,dst)

    else:
        exit(0)

# Main Script
parser = argparse.ArgumentParser(description='Script for prepping data for injection into LE and then grading.')
parser.add_argument('-n', '--nab_data', default=False, required=False, action='store_true', help='default data has labels and timeseries data')
parser.add_argument('-har', '--harvard_data', default=False, required=False, action='store_true', help='harvard data, labels no timeseries')
parser.add_argument('-t', '--timeseries', default=False, required=False, action='store_true', help='If dataset is timeseries but no labels')
parser.add_argument('-p', '--process_only', default=False, required=False, action='store_true', help='If flag is enabled it will move to only process the data and will NOT create the injection files.')
parser.add_argument('-c', '--chart', default=False, required=False, action='store_true', help='Plotting disabled by default, set flag to enable')
args = parser.parse_args()

if args.nab_data:
    print "sorting label data for NAB"
    nab_data()
elif args.harvard_data:
    print "adding timeseries to harvard data"
    harvard_data()
elif args.timeseries:
    print "data does have timeseries data but no labels"
    timeseries()
elif args.process_only:
    print "Not creating injection files - processing LE files only"
    processing()
elif args.chart:
    print "Plotting enabled"
    plot # calls plot.py

