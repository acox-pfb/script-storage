from pathlib import Path
import os
import subprocess

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

def ExtractSitRep2A(file):
        basename = os.path.splitext(os.path.basename(file))[0]
        path = os.path.dirname(file)
        inputFile = open(file);
        outputFile = open(path+ "\\" +basename + ".SITREP2A.LOG", 'w')

        for row in inputFile:
            if "SITREP2A" in row:
                index = row.index("#SITREP2A")
                outputFile.write(row[index:])
        
        inputFile.close()
        outputFile.close()
        

startDir = "D:\\PNTAX2022\\Process\\DF\Day228"

subfolders, files = run_fast_scandir(startDir, [".LOG"])
for file in files:
    ext = os.path.splitext(os.path.basename(file))[1]
    if ".LOG" in ext:
            basename = os.path.splitext(os.path.basename(file))[0]
            path = os.path.dirname(file)
            
            if "NTV-GAJT" in file:
                print("Stripping Sitrep2A from " + file)
                ExtractSitRep2A(file)


