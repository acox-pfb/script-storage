from pathlib import Path
import os
import re
import subprocess
import sys

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].upper() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def getTruthFile(truthFiles, day, scenario, antenna):
    antennaMatches = [match for match in truthFiles if antenna in match]
    scenarioMatches = [match for match in antennaMatches if scenario in match]
    matches = [match for match in scenarioMatches if day in match]
    if len(matches) == 0:
        print("No matches found for: "+ day + " " + scenario + " " + antenna)
        return None
    elif len(matches) == 1:
        return matches[0]
    else:
        print("Multiples matches found for: " + day + " " + scenario + " " + antenna)
        return None
    
def getFilesForTruthing(day, scenario, fileList):
    
    dayMatches = [match for match in fileList if day in match]
    scenarioMatches = [match for match in dayMatches if scenario in match]
    
    return scenarioMatches

def processStats(path, basename, rtposvelDir, startTime, endTime):
    #Open InstPerr.Git
    totalEpochs = 0
    numEpochs = 0
    numEpochsUnderLimit = 0
    ERRORLIMIT = 10.00
    
    startData = False
    Error3D = {}
    try:
        instPerrFile = open(rtposvelDir + "\\InstPerr.Git", 'r')
    except Exception as err:
        return [0,0, 0, 0, 0, 0]

    for line in instPerrFile:
        if "[data]" in line:
            startData = True
            continue

        if startData == True:
            fields = line.split(",")
            totalEpochs += 1
            if float(fields[0]) > startTime and float(fields[0]) < endTime:
                numEpochs += 1
                if float(fields[9]) <= ERRORLIMIT:
                    numEpochsUnderLimit += 1
    
    totalBestposLines = 0
    totalBestposLinesWithinTimeFrame = 0
    numBestposSolution = 0
    #Open ASCII BestPos File
    bestposFile = open(path + "\\" + basename + "\\ASCII\\" + basename + ".BIN.ascii.BESTPOS")

    for line in bestposFile:
        totalBestposLines += 1
        log = line.split(';')
        header = log[0].split(',')
        message = log[1].split(',')
        if float(header[6]) >= startTime and float(header[6]) <= endTime:
            totalBestposLinesWithinTimeFrame += 1
            if message[0] == "SOL_COMPUTED":
                numBestposSolution += 1

    print(basename)
    print("Total BestPos Lines: " + str(totalBestposLines))
    print("Total BestPos within TimeFrame solution: " + str(totalBestposLinesWithinTimeFrame))
    print("Total BestPos with computed solution: " + str(numBestposSolution))
    print("Total RTPOSVEL Epochs: " + str(totalEpochs))
    print("Total RTPOSVEL within timeframe: " + str(numEpochs))
    print("Total Epochs < " + str(ERRORLIMIT) + ": " + str(numEpochsUnderLimit))
    return [totalBestposLines,totalBestposLinesWithinTimeFrame, numBestposSolution, totalEpochs, numEpochs, numEpochsUnderLimit]

def get3DStats(path, basename):
    subfolders, files = run_fast_scandir(path, [".SUM"])
    if len(files) != 1:
        print("Incorrect number of summary files found")
        raise ValueError("Incorect number of summary files")
    
    #Open the summary file and extract the 3D RMS values
    rtposVelSummary = open(files[0], 'r')
    hitUnfiltered = False
    rms3D = ""
    min3D = ""
    max3D = ""
    numPoints = ""
    for line in rtposVelSummary:
        if "UNFILTERED position error statistics for unmatched position logs" in line:
            hitUnfiltered = True
            continue
        if hitUnfiltered == True:
            if "RMS(m):" in line:
                rmsValues = line[19:].split()
                rms3D = rmsValues[0].strip()
                continue
            if "Max Value(m)" in line:
                maxVlues = line[19:].split()
                max3D = maxVlues[0].strip()
                continue
            if "Min Value(m)" in line:
                minValues = line[19:].split()
                min3D = minValues[0].strip()
                continue
            if "Num. Points" in line:
                numPointsValues = line[19:].split()
                numPoints = numPointsValues[0].strip()
                return [rms3D, min3D, max3D, numPoints]
    
    return ["0","0","0","0"]
    

routeTimes = {
    "261_FIVE-CT-HIGH"      :   [202261,    206724],
    "261_ONE-CT-LOW"        :   [196269,    200503],
    "261_THREE-CT-LOW"      :   [207901,    211821],
    "262_FIVE-CT-HIGH-ET"   :	[288793,	292850],
    "262_ONE-CT-HIGH-ET"    :	[298977,	302962],
    "262_ONE-CT-LOW-ET"     :   [283144,    287284],
    "262_THREE-CT-LOW-ET"   :   [293634,	297936],
    "263_FIVE-CT-HIGH-ET"   :   [375560,    379800],
    "263_THREE-CT-HIGH-ET"  :   [369412,    373785],
    "264_RASPBERRY-ONE"     :   [455398,    461109],
    "264_RASPBERRY-PIE-ONE" :   [467324,   	469388],
    "264_RASPBERRY-PIE-TWO" :   [470500,	473106],
    "265_RASPBERRY-ONE"     :   [541400,	546996],
    "265_RASPBERRY-PIE-TWO" :   [554103,	555895],
    "267_BLUEBERRY-ONE_RUN1":   [153531,    157338],
    "267_BLUEBERRY-ONE_RUN2":   [158381,    162026],
    "267_BLUEBERRY-ONE_RUN3":   [162494,	164895],
    "268_BLUEBERRY-TWO_RUN1":   [241097,    244394],
    "268_BLUEBERRY-TWO_RUN2":   [245315,    248864],
    "268_BLUEBERRY-TWO_RUN3":   [249319,	251699],
    "269_BLUEBERRY-THREE_RUN1":   [325068,    328738],
    "269_BLUEBERRY-THREE_RUN2":   [330162,    333826],

}

startTime = 0
stopTime = 0


rtposvelCmd = "rtposvel /GAL /KML "

startDir = "D:\\PNTAX24\\Processing"
truthDir = "D:\\PNTAX24\\Processing\\Truth"
rtposvelDir = "D:\\PNTAX24\\Processing\\RTPOSVEL"

truthSubfolder, truthFiles = run_fast_scandir(truthDir, [".TXT"])

statsFile = open(startDir + "\\stats.csv", 'w')
statsFile.write("File, TruthFile, Day, Receiver, Antenna, Scenario, Total_BestPos, TotalBestposLinesWithinTimeFrame, Total_BestPos_Computed, Total_RTPOSVEL_Epochs, Total_RTPOSVEL_TimeFrame, TotalEpochsUnderLimit, RMS3D(m), Min3D(m), Max3D(m), RTPosVelCount\r")

subfolders, files = run_fast_scandir(startDir, [".BIN"])

if not os.path.exists(rtposvelDir):
    subprocess.call("mkdir " + rtposvelDir, shell=True)

#Get a key and find the files needed for that truth
for key in routeTimes:
    times = routeTimes[key]
    startTime = times[0]
    endTime = times[1]
    dayScenario = str.split(key, "_")
    day = dayScenario[0]
    scenario = dayScenario[1]

    
    fileList = getFilesForTruthing(day,scenario, files)
 

    for file in fileList:
        if "BinarySubmit" in file:
            continue

        basename = os.path.splitext(os.path.basename(file))[0]
        path = os.path.dirname(file)
        ext = os.path.splitext(os.path.basename(file))[1]

    
        if "UBLOX" in file:
            print("Not Processing Ublox file")
            continue

        if "STATIC" in file:
            print("Not processing Static file")
            continue

        if "SEPTENTRIO" in file:
            print("Not processing Septentrio files")
            continue

        
        if "Truth" in path:
            continue

        name = str.split(basename, "_")
        print(name)
        day = name[0]
        participant = name[1]
        systemFields = str.split(name[2], "-")
        print(str.split(name[2], "-"))

        receiver = systemFields[1]
        #platform = systemFields[0]
        receiverOptions = systemFields[2]
        antenna = systemFields[3]



        scenario = name[3]
        route = name[4]
        print(scenario, route)

        #This is needed to get the correct truth file for the GPR
        if receiver == "PWRPAK7E2":
            antenna = "GPR"

        if "ITK" in receiverOptions:
            continue

        scenarioRun = scenario
        newDir = "RTPOSVEL_" + basename

        if len(dayScenario) == 3:
            newDir += "_" + dayScenario[2]
            scenarioRun += "_" + dayScenario[2]

        if day == "263":
            print("Day 263")

        truthFile = getTruthFile(truthFiles, day, scenario, antenna)
        if truthFile == None:
            print("ERROR: No Truth File for: " + basename)
            continue

        rtposvelPath = rtposvelDir + "\\" + newDir

        if os.path.exists(rtposvelPath):
            print("Folder Exists, skipping: " + newDir)
        else:
            print("File :" + file + "\r\nTruth: " + truthFile + "\r\n")
            subprocess.call("mkdir " + rtposvelPath, shell=True)
            rtposvelCall = "rtposvel /GAL /KML /ts " + str(startTime) + " /tp " + str(endTime) + " /gn " + truthFile + " " + file
            subprocess.call(rtposvelCall, shell=True, cwd=rtposvelPath)

        stats = processStats(path, basename, rtposvelPath, startTime, endTime)
        stats3D = get3DStats(rtposvelPath, basename)
        statsFile.write(basename + "," + os.path.splitext(os.path.basename(truthFile))[0] + "," + day + "," + receiver + "," + antenna + "," + scenarioRun + "," + str(stats[0]) + "," + str(stats[1]) + "," + str(stats[2]) + "," + str(stats[3]) + "," + str(stats[4]) + "," + str(stats[5]) + "," + stats3D[0] + "," + stats3D[1] + "," + stats3D[2] + "," + stats3D[3] + "\r")
    

statsFile.close()            




