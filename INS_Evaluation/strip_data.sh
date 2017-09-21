#/bin/bash!

#######
# This script will be used to strip data from the GPS and INS logged files 
# GGA: column 7, 8, 9
# GST: column 4 and 5 (SD semi-major/minor)
# INS STS: column 4
# Filename format:
# GPS file name has to be GPS_LOG.txt
# INS file name has to be INS_LOG.txt
##

mkdir c:/temp
cd c:/temp/
echo "Current working directory: " 
pwd
#echo " Enter file location:"
#read inp
#cd $inp
ls

grep GGA GPS_Log.txt > zGGA
cat zGGA | cut -d , -f 7 > GPS-quality
cat zGGA | cut -d , -f 8 > GPS-sats       
cat zGGA | cut -d , -f 9 > GPS-HDOP  

 
grep GGA INS_Log.txt > zINS_GGA
cat zINS_GGA | cut -d , -f 7 > INS-quality
cat zINS_GGA | cut -d , -f 8 > INS-sats       
cat zINS_GGA | cut -d , -f 9 > INS-HDOP  

grep GST GPS_Log.txt >zGST
cat zGST | cut -d , -f 4 > GPS-semi-maj
cat zGST | cut -d , -f 5 > GPS-semi-minor

grep GST INS_Log.txt > zINS_GST
cat zINS_GST | cut -d , -f 4 > INS-semi-maj
cat zINS_GST | cut -d , -f 5 > INS-semi-minor

grep STS INS_Log.txt > zSTS
cat zSTS | cut -d , -f 4 > HDG


gnuplot plot.dat



rm z* GPS-* INS-* HDG
