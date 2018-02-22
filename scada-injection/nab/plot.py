#!/usr/bin/python
import os, glob, csv
import numpy as np
import random
import shutil
import matplotlib
import matplotlib.pyplot as plt

#Plot numenta data

datasets=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets/tmpFiles/")
NABFiles=("/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets")
os.chdir(datasets)

for dirName in glob.glob('z*'):
    #print dirName
    fname = dirName[1:]
    os.chdir(datasets+'/'+dirName)
    for f in glob.glob('Plotting-Sev*.csv'):
        print "Plotting: {}: {}".format(dirName, f)
        x1=[]
        x2=[]
        x3=[]
        with open(f,'r') as csvfile:
            #print dirName
            plots = csv.reader(csvfile, delimiter=',')
            csvfile.readline()
            for row in plots:
                   
                # print f
                x1.append(float(row[0]))
                x2.append(float(row[1]))
                x3.append(float(row[2]))
            num_lines = sum(1 for line in open(f))
            #print num_lines   
            quarter = num_lines/4
            half = num_lines/2
            threeQuart = quarter+half
            #print quarter, half, threeQuart 

        fig = plt.figure()
        fig.set_figwidth(12)
        fig.set_figheight(10)
        plt.xticks([]) # hide x and y ticks on figure.
        plt.yticks([])
        plt.title(dirName+f)

        matplotlib.rc('xtick', labelsize=8)
        matplotlib.rc('ytick', labelsize=8)
        fig.text(0.05, 0.5, 'Anomaly Values', va='center', rotation='vertical')
        fig.text(0.95, 0.5, 'Label:0-1', va='center', rotation='vertical')

        ax1 = fig.add_subplot(411)
        plt.xlim(0, quarter)
        lns1 = ax1.plot(x1, color='grey', label="Raw Data")
        lns2 = ax1.plot(x2, color='r', label="HGR Data")
        ax2 = ax1.twinx()
        ax2.set_xlim(0,quarter)
        ax2.set_ylim(0.2,1.5)
        lns3 = ax2.plot(x3, color='b', label="labels")
        #fig.tick_params(labelsize=10)


        ax3 = fig.add_subplot(412)
        plt.xlim(quarter, half)
        ax3.plot(x1, color='grey', label="Raw Data")
        ax3.plot(x2, color='r', label="HGR Data")
        ax4 = ax3.twinx()
        ax4.set_xlim(quarter, half)
        ax4.set_ylim(0.2,1.5)
        ax4.plot(x3, color='b', label="labels")


        ax5 = fig.add_subplot(413)
        plt.xlim(half, threeQuart)
        ax5.plot(x1, color='grey', label="Raw Data")
        ax5.plot(x2, color='r', label="HGR Data")
        ax6 = ax5.twinx()
        ax6.set_xlim(half, threeQuart)
        ax6.set_ylim(0.2,1.5)
        ax6.plot(x3, color='b', label="labels")
         

        ax7 = fig.add_subplot(414)
        plt.xlim(threeQuart, num_lines)
        ax7.plot(x1, color='grey', label="Raw Data")
        ax7.plot(x2, color='r', label="HGR Data")
        ax8 = ax7.twinx()
        ax8.set_xlim(threeQuart, num_lines)
        ax8.set_ylim(0.2,1.5)
        ax8.plot(x3, color='b', label="labels")
       

        lns = lns1+lns2+lns3
        labs = [l.get_label() for l in lns]
        box = ax7.get_position()
        ax7.set_position([box.x0, box.y0, box.width, box.height])
        ax8.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=3)
        plt.savefig(fname+f+'.png')
        #plt.show()

print " Organising Files Now"
os.chdir(datasets)


for f in glob.glob('zart_daily_no_*/*.png'):
    shutil.move(f, NABFiles+'/artificialNoAnomaly')
for f in glob.glob('zart_daily_perf*/*.png'):
    shutil.move(f, NABFiles+'/artificialNoAnomaly')
for f in glob.glob('zart_daily_smal*/*.png'):
    shutil.move(f, NABFiles+'/artificialNoAnomaly')
for f in glob.glob('zart_flatline*/*.png'):
    shutil.move(f, NABFiles+'/artificialNoAnomaly')
for f in glob.glob('zart_noisy*/*.png'):
    shutil.move(f, NABFiles+'/artificialNoAnomaly')

for f in glob.glob('zart_daily_flat*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsd*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')
for f in glob.glob('zart_daily_jumpsu*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')
for f in glob.glob('zart_daily_noj*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')
for f in glob.glob('zart_increase*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')
for f in glob.glob('zart_load*/*.png'):
    shutil.move(f, NABFiles+'/artificialWithAnomaly')

for f in glob.glob('zexchange*/*.png'):
    shutil.move(f, NABFiles+'/realAdExchange')

for f in glob.glob('zec2_c*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('zec2_d*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('zec2_n*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('zelb*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('zgro*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('ziio*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')
for f in glob.glob('zrds*/*.png'):
    shutil.move(f, NABFiles+'/realAWSCloudwatch')

for f in glob.glob('zambient*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')
for f in glob.glob('zcpu_u*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')
for f in glob.glob('zec2_r*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')
for f in glob.glob('zmachine*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')
for f in glob.glob('znyc*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')
for f in glob.glob('zrogue*/*.png'):
    shutil.move(f, NABFiles+'/realKnownCause')

for f in glob.glob('zocc*/*.png'):
    shutil.move(f, NABFiles+'/realTraffic')
for f in glob.glob('zspeed*/*.png'):
    shutil.move(f, NABFiles+'/realTraffic')
for f in glob.glob('zTravel*/*.png'):
    shutil.move(f, NABFiles+'/realTraffic')

for f in glob.glob('zTwitt*/*.png'):
    shutil.move(f,NABFiles+'/realTweets')