#!/bin/bash
# will run until it's finished
x=100000

for i in `ls /VideoLibrary/DITesting/Alert-per-feature/`; do
	echo $i $x
	redis-cli -s /tmp/omniai_redis_msgbus.sock monitor > $i-msgbus.log &
	tpid=$!
#	echo $tpid
	python /home/omniai/data_gen/videoPlaybackDriver.py /VideoLibrary/DITesting/Alert-per-feature/$i -s 0.01 -i $x 
	kill $tpid
#	python /home/aisight/graydient/data_gen/videoPlaybackDriver.py $i -i $x &
	$((x++))
#	echo $x
done




