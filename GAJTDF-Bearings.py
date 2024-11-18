#
# this strips teh time and GAJT bearing value from GAJT-TIMES.DAT files
# 710 and 410 use relative bearing in SITREP2: fields 13 and 27
# 310 SITREP3 use relative bearing in degrees
#
# Get vehicle ref LAT LON from *PWRPAK7-SPAN-GNSS850*.BESTPOS file

import os, glob
import math

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

def ntv1():
    startDir = "D:\\PNTAX24\\DF"
    brgFile = "D:\\PNTAX24\\Processing\\GAJT-TIMES"

    subfolders, files = run_fast_scandir(brgFile, [".DAT"])
    #print(files)
    for file in files:
        ext = os.path.splitext(os.path.basename(file))[1]

        if ".DAT" in ext:
                basename = os.path.splitext(os.path.basename(file))[0] #name of the file
                path = os.path.dirname(file) #file path
                day = basename.split('_')[0]
                system = basename.split('_')[2]
                gajt = system.split('-')[1]
                scenario = basename.split('_')[3]

                #print(day, gajt, scenario)
                brgFile = open(startDir + "\\" + basename + ".csv", 'w')
                brgFile.write("time, L1Brg, L1Status, L2Brg, L2Status\r")


                if gajt == "GAJT710" or gajt == "GAJT410":
                    print(basename)
                    with open(path + "\\" + basename + ".DAT", "r") as f:
                        #print(path + "\\" + basename + ".DAT")
                        for line in f:
                            if line.startswith("#SITREP2A"):
                                timeField = line.split(";")[0].split(",")[7]
                                #print(timeField)
                                time = float(timeField)/1000
                                L1Brg= line.split(",")[13]
                                L1 = line.split(",")[17]
                                if L1 == "YES":
                                    L1Status = 1
                                else:
                                    L1Status = 0
                                L2Brg = line.split(",")[23]
                                L2 = line.split(",")[27]
                                if L2 == "YES":
                                    L2Status = 1
                                else:
                                    L2Status = 0
                                #print(basename, time, L1Brg, L1Status, L2Brg, L2Status)
                                brgFile.write(str(time) + "," + L1Brg + "," + str(L1Status) + "," + L2Brg + "," + str(L2Status) + "\r")
            
                if gajt == "GAJT310" :
                    print("NOT READY YET", basename)

if __name__ == "__main__":
    ntv1()