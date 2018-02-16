#!/bin/bash

#call this file to organize the raw dataset so:
#  last 27k 'normal' lines are moved to the head
#  remained of outlier and normal are shuffled

datasets="/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets"
maturityPoints=1100
cd $datasets
for x in `ls *.tab`
do 
   var=$(less $x | wc -l)
   echo $var
   rest=$((var-maturityPoints))
   echo $rest
   head -n $rest $x > end
   cat end | shuf > tail
   tail -n $maturityPoints $x > head

   cat head tail > all # contains 27k normal followed by shuffled outlier and normal
   rm head end tail

   # now to add timestamp and increment by 1000micro secs.
   for f  in 1514764800000 ; do sed -i "s/^/$f\t/" all; done
   awk '{$1=$1/1000;}1' all | awk 'BEGIN {OFS=FS} {$1=$1+(NR-1); print}'  > timestampFile.csv
   sed -i "s/ /,/g" timestampFile.csv
   awk -F ',' '{print $1}' timestampFile.csv > dates
   for d in `less dates`; do  printf '%(%F %T)T\n' $d >> YMD-hms; done
   rm all dates
   
   awk -F ',' -v OFS=',' '{$1=""}1' timestampFile.csv > tmp
   paste YMD-hms tmp > test
   sed  "s/\t//" test > tStampAndLabels # contains raw data with timestamp and labels
   cat -n tStampAndLabels > $x-forProcessing.csv #contains raw data, timestamps, labels and trackid
   awk -F ',' -v OFS=',' 'NF{NF--};1' tStampAndLabels > $x-readyForInjection.csv #contains timestamp and NO labels



   rm test tmp YMD-hms timestampFile.csv tStampAndLabels

   #now copy the readyForInjection.csv file to the machine for running.
   # produces a learning_0.log-$x-readyforInecjtion.csv which should be copied to LE-logs for further processing.


done
