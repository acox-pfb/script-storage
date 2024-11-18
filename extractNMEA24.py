# Python3
# Script to strip NMEA data from Septentrio, UBLOX and STL logs
# search and then open .DAT file and search for $G  to *12 strings and
# place them in NMEA.LOG FILE
#
# Call each type specificallly so it doesn't run through GAJT logs

import glob,   os, shutil
import extractHiddenLogsGAJT24


def main():

    for InputFile in glob.glob("*UBLOX*.DAT"):
        move(InputFile)
    for InputFile in glob.glob("*SEPTENTRIO*.DAT"):
        move(InputFile)
    for InputFile in glob.glob("*STL*.DAT"):
         move(InputFile)
    for InputFile in glob.glob("*PWRPAK*.DAT"):
        move(InputFile)
    for InputFile in glob.glob("*OEM7*.DAT"):
        move(InputFile)


def move(InputFile):
    filename = InputFile[:-4]
    jDay = filename[:3]
    print(jDay)
    dir = "path\\RawSubmittal" + '\\' + jDay
    isExist = os.path.exists(dir)
    if not isExist:
        os.makedirs(dir)
    os.system("nconvert-m6 --unknown-bytes=ignore -c=GPGGA,GPGLL,GPGSA,GPGSV,GPRMC,GPVTG,GPZDA  %s" % InputFile)
    os.remove(InputFile + ".ascii.log")
    NMEAfile = filename + ".NMEA.TXT"
    os.rename(InputFile + ".ascii", NMEAfile)
    print(NMEAfile)
    shutil.move(NMEAfile, dir)


if __name__ == "__main__":
    main()
