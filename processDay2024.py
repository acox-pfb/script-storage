from pathlib import Path
import os
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

def process():
    

    startDir = sys.argv[1]

    directoryNMEA = "\\NMEA"
    directory1Hz = "\\1HZ"
    directorySubmitBinary = "\\BinarySubmit"
    directoryUblox = "\\Ublox"
    directoryBestSats = "\\BestSats"
    
    


    nmeaCallCmd = "c:\\Utils\\HA_NConvert\\nconvert-m6 --ascii --no-seek-approximate-time --convert=GPGGA,GPGLL,GPVTG,GPGSA,GPGSV,GPRMC,GPZDA -o "
    decimateBinary = "c:\\Utils\\HA_NConvert\\nconvert-m6 --binary --decimate-solutions --decimate=RANGE,1000 --decimate=BASICPOS,1000 --decimate=BASICSATS,1000 --decimate=TIME,1000 --decimate=PSRSATS,1000 --decimate=BESTSATS,1000 --decimate=CAKESATS,1000 -o "
    submittalBinary = "c:\\Utils\\HA_NConvert\\nconvert-m6 --binary -c=VERSION,BESTPOS,BESTVEL,RANGE,BESTSATS,TIME,ITDETECTSTATUS,RAWIMUSX,INSPVAX -o "
    nconvertUbloxCallCmd = "c:\\Utils\\HA_NConvert\\nconvert-m6 --binary --convert-u-blox -o "
    aebConvertCallCmd = "c:\\Utils\\AEB_SkyPlot_ASCII_1Hz.bat "

    subfolders, files = run_fast_scandir(startDir, [".DAT"])
    for file in files:
        ext = os.path.splitext(os.path.basename(file))[1]

        if ".DAT" in ext:
                basename = os.path.splitext(os.path.basename(file))[0]
                path = os.path.dirname(file)
                #str.replace("RawData", "Processing")
                print(path)
                try:
                    os.makedirs(path+directoryNMEA)
                    os.makedirs(path+directory1Hz)
                    os.makedirs(path+directorySubmitBinary)
                    os.makedirs(path+directoryUblox)
                    os.makedirs(path+directoryBestSats)
                except FileExistsError:
                    print("Directory exists skipping")
                
                if "Truth" in path:
                    continue
                name = str.split(basename, "_")

                if "PWRPAK7" in file or "OEM725" in file or "UBLOX" in file or "SEPTENTRIO" in file or "STL" in file:
                    nmeaCall = nmeaCallCmd + path + directoryNMEA + "\\" + basename + "_NMEA.TXT " + file
                    ubcallReturn = subprocess.call(nmeaCall, shell=True)


                if "PWRPAK7" in file or "OEM725" in file:
                    decimateCall = decimateBinary + path + directory1Hz + "\\" + basename + "_1HZ.BIN " + file
                    subcallReturn = subprocess.call(decimateCall, shell=True)
                    submitBinaryCall = submittalBinary + path + directorySubmitBinary + "\\" + basename + ".BIN " + path + directory1Hz + "\\" + basename + "_1HZ.BIN" 
                    subcallReturn = subprocess.call(submitBinaryCall, shell=True)
                    aebCall = aebConvertCallCmd + path + directory1Hz + "\\" + basename + "_1HZ.BIN"
                    subcallReturn = subprocess.call(aebCall, shell=True, cwd=path)
                    os.chdir(path+directoryBestSats)
                
                    bestSatsFilePath = path + directory1Hz + "\\" + basename + "_1HZ\\ASCII\\" + basename + "_1HZ.BIN.ascii.BESTSATS"
                    if os.path.isfile(bestSatsFilePath):
                        subprocess.run("python \\processBestSats.py " + bestSatsFilePath)
                    
                        moveSource = path + directory1Hz + "\\" + basename + "_1HZ\\ASCII\\" + basename + "_1HZ.BIN.ascii_constellations.gitl"
                        moveDestination = path+directoryBestSats
                        subprocess.call("move " + moveSource + " " + moveDestination, shell=True )
                        moveSource = path + directory1Hz + "\\" + basename + "_1HZ\\ASCII\\" + basename + "_1HZ.BIN.ascii_frequencies.gitl"
                        subprocess.call("move " + moveSource + " " + moveDestination, shell=True )
                
                if "UBLOX" in file:
                    print("Processing Ublox Convert " + path + " " + file)
                    nconvertUbloxCall = nconvertUbloxCallCmd + path + directoryUblox +"\\" + basename + "_NOV.BIN " + file
                    subcallReturn = subprocess.call(nconvertUbloxCall, shell=True)

if __name__ == "__main__":
    process()
