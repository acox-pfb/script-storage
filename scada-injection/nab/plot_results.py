#!/usr/bin/python


import os

import pandas as pd
import matplotlib.pyplot as plt

import autoencoder
from utils.fileUtils import getfilepaths

from pprint import PrettyPrinter, pprint

doPlot = True

rows = 4 ## plotting raw scores (for autoencoder)
# rows = 3 ## no plotting raw scores (for autoencoder)

## 0.998672103882 for 'autoencoder_partial_mean'
defaultThreshold = 0.9999 # 0.999 # 0.998

resultNAB = '/home/acox/NAB/results/' ## root

## the default
myDetector = 'foundation' ## my detector is always the default
resultFolder = myDetector + '/'
rfDetector = 'numenta'
refernFolder = rfDetector + '/'

nabSortedFile = ''
nabSortedThresh = 100 # for all ### -0.5

args = os.sys.argv
if len(args) > 1:
    if args[1]:
        resultFolder = args[1] + '/'
    if len(args) > 2:
        if args[2]:
            rfDetector = args[2]
            refernFolder = rfDetector + '/'
        if len(args) > 3:
            if args[3]:
                defaultThreshold = float(args[3])
            if len(args) > 4:
                nabSortedFile = args[4]
                doPlot = False

fileKey_ae = resultNAB + resultFolder + '*/*.csv'
fileKey_rf = resultNAB + refernFolder + '*/*.csv'
resultFilePaths = getfilepaths(fileKey_ae)
refernFilePaths = getfilepaths(fileKey_rf)

def getThreshold (detector, folder):
    scorefile = resultNAB + folder + detector + '_standard_scores.csv'
    if os.path.isfile(scorefile):
        df = pd.read_csv(scorefile)
        return df['Threshold'][0]
    else:
        return defaultThreshold

resultThresh = getThreshold(myDetector, resultFolder)
refernThresh = getThreshold(rfDetector, refernFolder)

nabCompare = 0.0
nabSorted = []

def getReferenceFile (fn):
    return next(x for x in refernFilePaths if fn in x)

def plot_file (filename, count):

    global nabCompare

    fn = filename.split('/')[-1][len(myDetector):]
    fileReference = getReferenceFile(fn)
    if doPlot:
        print '   v.s. results in', fileReference

    dfRef = pd.read_csv(fileReference)
    df = pd.read_csv(filename)

    tsz = df['training_size'][0]
    cms = tsz + df['cdf_min_size'][0]

    if 'probationary_period' in df.columns:
        lsz = int(df['probationary_period'][0])
    else:
        ## @NOTE: see config "minseries" in "autoencoder_detector_full.py"
        # lsz = int(tsz * 2 + 32)
        lsz = int(tsz + df['cdf_min_size'][0] + 32)

    ## panel 1
    ## v = df['value']
    n = df['normalized_value']
    l = df['label']

    ## panel 2 - reference/comparison (e.g. numenta) score
    s_ = dfRef['anomaly_score']

    ## panel 3 - autoencoder score
    s = df['anomaly_score']

    ## panel 4 - autoencoder raw score
    r = df['raw_score']

    assert(len(s) == len(s_))
    assert(len(s) == len(r))
    assert(len(s) == len(n))
    assert(len(s) == len(l))

    ## estimate & compare NAB scores
    s_nab = estimateNABScore(s[lsz:], l[lsz:], resultThresh)
    s_nab_ = estimateNABScore(s_[lsz:], l[lsz:], refernThresh)
    diff_nab = s_nab - s_nab_
    nabCompare += diff_nab
    fn = fn[1:]
    nabSorted.append((fn, diff_nab))

    if doPlot:

        x = range(len(s))

        ### fmng = plt.get_current_fig_manager()
        ### fmng.window.showMaximized()
        plt.figure(figsize = (24, 12))

        '''
        plt.subplot(rows, 1, 1)
        plt.plot(x, v, c = 'b', linewidth = 1.5)
        plt.plot(x, v * l, c = 'r', linewidth = 2)
        plt.title(str(count) + '. ' + filename)
        '''
        plt.subplot(rows, 1, 1)
        plt.plot(x, n, c = 'k', linewidth = 1.5)
        plt.plot(x, l, c = 'r', linewidth = 3)
        plt.title(str(count) + '. ' + filename)
        ## plt.title('normalized value, label')

        plt.subplot(rows, 1, 2)
        plt.plot(x, s_, c = 'r', linewidth = 2)
        plt.plot([0,len(x)], [refernThresh, refernThresh], c = 'k', linewidth = 0.9)
        plt.plot([lsz, lsz], [0, 1], c = 'k', linewidth = 3.6, linestyle = '--')
        plotAnomalyMarkers(s_, refernThresh)
        plt.title(rfDetector + ' Anomaly Score, ' + str(s_nab_))
        plt.ylim(refernThresh - 0.1, 1.1)

        plt.subplot(rows, 1, 3)
        plt.plot(x, s, c = 'r', linewidth = 2)
        plt.plot([0,len(x)], [resultThresh, resultThresh], c = 'k', linewidth = 0.9)
        plt.plot([lsz, lsz], [0, 1], c = 'k', linewidth = 3.6, linestyle = '--')
        plotAnomalyMarkers(s, resultThresh)
        plt.title(myDetector + ' Anomaly Score, ' + str(s_nab))
        # plt.ylim(0.9995, 1.0005)
        # plt.ylim(0.99, 1.01)
        plt.ylim(resultThresh * 0.999, resultThresh * 1.001)

        if rows == 4:
            plt.subplot(rows, 1, 4)
            plt.plot(x, r, c = 'r', linewidth = 2)
            r1 = min(r); r2 = max(r)
            plt.plot([tsz, tsz], [r1, r2], c = 'b',
                     linewidth = 1.8, linestyle = '--')
            plt.plot([cms, cms], [r1, r2], c = 'k',
                     linewidth = 1.8, linestyle = '--')
            plt.title(myDetector + ' Raw Score')

            plt.show()

    return fn

def estimateNABScore (scores, labels, thresh):

    assert(len(scores) == len(labels))
    sl = zip(scores, labels)

    alertScored = False
    result = 0.0

    for s, l in sl:
        alertOn = (s >= thresh)
        if l and alertOn and (not alertScored):
            alertScored = True
            result += 1.0
        elif (not l):
            alertScored = False
            result -= int(alertOn) * 0.11

    return result

def plotAnomalyMarkers (s, threshold):
    marks = [(i, v) for i, v in enumerate(s) if v >= threshold]
    xs = map(lambda z: z[0], marks)
    ys = map(lambda z: z[1], marks)
    plt.plot(xs, ys, c = 'b', marker = 'o', linestyle = 'None',)

if __name__ == '__main__':

    count = 0

    print 'Got', len(resultFilePaths), '(out of 58) results'
    for filename in resultFilePaths:
        count += 1
        if doPlot:
            print str(count) + '.', 'Plotting results in', filename
        fn = plot_file(filename, count)
        print '  ', fn, nabCompare

    nabSorted.sort(key = lambda x: x[1])
    pp = PrettyPrinter(indent = 1)
    pp.pprint(nabSorted)

    print "Total Comparison Score:", sum([x[1] for x in nabSorted])

    if nabSortedFile:
        nabSorted_ = [x for x in nabSorted if x[1] < nabSortedThresh]
        with open(nabSortedFile, 'w') as out:
            ### pprint(nabSorted, stream = out)
            pprint(nabSorted_, stream = out)
