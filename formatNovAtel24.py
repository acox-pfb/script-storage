#
#  Go to each _PWRPAK and _OEM7 .DAT file and run nconvert to strip out only:
#  BESTPOS,BESTSATS,BESTVEL,BESTXYZ,ITDETECTSTATUS,RANGE,SATVIS2,TIME messages
#  nconvert-m6 --unknown-bytes=ignore -c=BESTPOS,BESTSATS,BESTVEL,BESTXYZ,ITDETECTSTATUS,RANGE,SATVIS2,TIME -b --ignore-CRC *.DAT

import glob, os, shutil
import extractNMEA24

current = os.getcwd()

def main():
    for x in glob.glob("*PWRPAK*.DAT"): # and do the same for *_OEM7*.DAT
        #os.chdir(os.path.dirname(x)) #change to the directory where the folder being converted resides.
        print(x)
        y = x[:-4]+".BIN"
        jDay = x[:3]
        print(jDay)
        dir = "D:\\PNTAX24\\HHAnowSECURESTART\\RawSubmittal"+'\\'+jDay+'\\'+"NOVATELBINARY"
        isExist = os.path.exists(dir)
        if not isExist:
            os.makedirs(dir)
        os.system("c:\\Utils\\HA_NConvert\\nconvert-m6  --unknown-bytes=ignore -b --decimate-solutions --decimate=RANGE,1000 --decimate=BASICPOS,1000 --decimate=BASICSATS,1000 --decimate=TIME,1000 --decimate=PSRSATS,1000 --decimate=BESTSATS,1000 --decimate=CAKESATS,1000 -c=VERSION,BESTPOS,BESTVEL,RANGE,BESTSATS,TIME,ITDETECTSTATUS,RAWIMUSX,INSPVAX --ignore-CRC %s" %x)
        #os.remove(x + ".binary.log")
        shutil.move(x + ".binary.log", dir)
        os.rename(x + ".binary", y)
        shutil.move(y,dir)
        print(dir)

    for x in glob.glob("*-OEM7*.DAT"): # and do the same for *_OEM7*.DAT
        #os.chdir(os.path.dirname(x)) #change to the directory where the folder being converted resides.
        print(x)
        y = x[:-4]+".BIN"
        jDay = x[:3]
        print(jDay)
        dir = "..\RawSubmittal" + '\\' + jDay + '\\' + "NOVATELBINARY"
        if not isExist:
            os.makedirs(dir)
        print(y)
        os.system("c:\\Utils\\HA_NConvert\\nconvert-m6  --unknown-bytes=ignore -b --decimate-solutions --decimate=RANGE,1000 --decimate=BASICPOS,1000 --decimate=BASICSATS,1000 --decimate=TIME,1000 --decimate=PSRSATS,1000 --decimate=BESTSATS,1000 --decimate=CAKESATS,1000 -c=VERSION,BESTPOS,BESTVEL,RANGE,BESTSATS,TIME,ITDETECTSTATUS,RAWIMUSX,INSPVAX --ignore-CRC %s" %x)
        #os.remove(x + ".binary.log")
        shutil.move(x + ".binary.log", dir)
        os.rename(x + ".binary", y)
        shutil.move(y, dir)
        print(dir)


if __name__ == "__main__":
    main()
