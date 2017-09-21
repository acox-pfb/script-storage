REM #######
REM # This script will be used to strip data from the GPS and INS logged files 
REM # GGA: column 7, 8, 9
REM # GST: column 4 and 5 (SD semi-major/minor)
REM # INS STS: column 4
REM # Filename format:
REM # GPS file name has to be GPS_LOG.txt
REM # INS file name has to be INS_LOG.txt
REM ##

md c:/temp
cd c:/temp/
Write-Host "Current working directory: " 
pwd
REM #echo " Enter file location:"
REM #read inp
REM #cd $inp
ls

select-string "GGA" GPS_Log.txt > zGGA
get-content .\zGGA | %{ $_.split(',')[7]; } > GPS-quality
get-content .\zGGA | %{ $_.split(',')[8]; } > GPS-sats       
get-content .\zGGA | %{ $_.split(',')[9]; } > GPS-HDOP  

select-string "GGA" INS_Log.txt > zINS_GGA
get-content .zINS_GGA | %{ $_.split(',')[7]; } > INS-quality
get-content .zINS_GGA | %{ $_.split(',')[8]; } > INS-sats       
get-content .zINS_GGA | %{ $_.split(',')[9]; } > INS-HDOP  

select-string "GST" GPS_Log.txt > zGST
get-content .zGST | %{ $_.split(',')[4]; } > GPS-semi-maj
get-content .zGST | %{ $_.split(',')[5]; } > GPS-semi-minor

select-string "GST" INS_Log.txt > zINS_GST
get-content .zINS_GST | %{ $_.split(',')[4]; } > INS-semi-maj
get-content .zINS_GST | %{ $_.split(',')[5]; } > INS-semi-minor

select-string "STS" INS_Log.txt > zSTS
get-content .zSTS | %{ $_.split(',')[4]; } >HDG

gnuplot plot.dat



rm z* GPS-* INS-* HDG
