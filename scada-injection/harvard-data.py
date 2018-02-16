#!/usr/bin/python
"""
 Provide user a choice - edit raw data for LE injection or process files for plotting and comparison:
 Edit for injection:
 Using harvard data stip last 11100 lines and set to head of file.
 shuffle remaining data in file and add to tail.
 remvoe labels

 Edit for Processing:
 stip HGR from LE file
 padd score with 0 for no hgr values
 plot raw values with HGR overlaid.
 plot outliers with HGR overlaid

 Create hgr with labels
 create hgr with raw

"""
import os
import glob
import random
import shutil
import fileinput
import csv
from collections import deque




datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets/harvard-edu-datasets")

os.chdir(datasets)

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    dirName = 'z'+f[:-7]
    print dirName, f
    if os.path.exists(dirName):
        shutil.rmtree(dirName)
    os.mkdir(dirName)
    with open(f)as fin, open(dirName+'/'+f+'-head.csv', 'w') as head:
        writer = csv.writer(head, delimiter = ' ')
        num_lines = sum(1 for line in open(f))
        #print f, num_lines
        last10 = deque(fin, 1100)
        writer.writerow(last10)
        #print >> head, last10
        tail = num_lines-1100
        #print f, tail
        with open (f) as rest, open(dirName+'/'+f+'-tail.csv', 'w') as t:
            for i in range(tail):
                line = rest.next().strip()
                print >> t, line
                #print t
            t.close()

print "NEXT"      
tails=[] # shuffle
for dName in glob.glob('z*'):
    #print dName
    os.chdir(datasets+'/'+dName)
    for f in glob.glob('*tail.csv'):
        tails.append(f)
        #print f
        fid  = open(f)
        li = fid.readlines()
        fid.close()
        random.shuffle(li)
        fid = open(f[:-9]+'-shuffled.csv', 'w')
        fid.writelines(li)
        fid.close

# merge head and shuffled together and then sart formatting for injection and plotting

for dirName in glob.glob('z*'):
    print dirName
    os.chdir(datasets+'/'+dirName)
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f in glob.glob('*head*'):
            head = f
            print head
        elif f in glob.glob('*shuff*'):
                shuff = f
                print shuff
    with open('edited-'+dirName, 'w')as edit:
        fin = fileinput.input(head, shuff)
        for line in fin:
            edit.write(line)
     





                
       
    
   
    