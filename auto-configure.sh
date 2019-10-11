#! /bin/bash


: '
script to ask:
what port to conect too
the imu orientaion in relation to teh vehciel frame


to then send setinstranslation
'


rm msg.txt

echo -e "Press 1 to Connect to receiver in terminal session\nPress 2 to configure SPAN" 
read selection

if [ $selection -eq "1" ]
then
	echo -n "what IP and port to  connect too? "; read port

	nc $port 
	# connect to port and allows user to type commands into receiver.
	# press CTRL-C to exit and quit.
	while read -r cmd; do
		echo ""
	done 
else

 echo -n  "What IP and port to  connect too? ";  read port_span
 
 echo -e "\n<<<<<<<<<<<<<<<<<<<<<<o>>>>>>>>>>>>>>>>>>>>>>>"

 echo -e "\nIMU orientation with refernce to vehice Frame"
 echo -e "\nType A: X right, Y forward, Z up    Type B: X forward, Y left, Z up     Type C: X left, Y back, Z up       Type D: X back, Y right, Z up"
 echo -e "Type E: X right, Y back, Z down     Type F: X forward, Y right, Z down  Type G: X left, Y forward, Z down  Type H: X back, Y left, Z down"
 echo -e "Type I: X down, Y forward, Z right  Type J: X down, Y left, Z forward   Type K: X down, Y back, Z left     Type L: X down, Y left, Z back"
 echo -e "Type M: X up, Y forward, Z left     Type N: X up, Y left, Z back        Type O: X up, Y back, Z right      Type P: X up, Y right, Z forward"
 echo -e "Type Q: X right, Y up, Z back       Type R: X forward, Y up, Z right    Type S: X left, Y up, Z forward    Type T: X back, Y up, Z left"
 echo -e "Type U: X right, Y down, Z forward  Type V: X forward, Y down, Z left   Type W: X left, Y down, Z back     Type X: X back, Y down, Z right\n"

 
 echo -n "Enter rotation type: "; read rotation
 echo -e "\n<<<<<<<<<<<<<<<<<<<<<<o>>>>>>>>>>>>>>>>>>>>>>>"
 if [[ $rotation != [A-X] ]];
 then 
 	echo "wrong selction, exiting now"
 	exit 0
 fi
 # ask for lever arms
 echo -ne "\nEnter X Y Z from IMU to Antenna1 in IMU frame "; read lever_arm

 echo -ne "\nEnter X Y Z from IMU to Antenna2 in IMU frame, input 0 if none " ; read lever_arms

 if [ $lever_arms -eq "0" ]
 then
	echo "SETINSTRANSLATION ANT1 $lever_arm" > msg.txt
 else
	echo "SETINSTRANSLATION ANT1 $lever_arm" > msg.txt
	echo "SETINSTRANSLATION ANT2 $lever_arms" >> msg.txt
 fi 

 # create a msg.txt file to send to the receiver once we know the orientation
 #echo $rotation

 case $rotation in
	A)
		echo "SETINSROTATION RBV 0 0 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	B)
		echo "SETINSROTATION RBV 0 0 -90" >> msg.txt
		nc $port_span < msg.txt
		;;
	C)
		echo "SETINSROTATION RBV 0 0 180 " >> msg.txt
		nc $port_span < msg.txt
		;;
	D)	
		echo "SETINSROTATION RBV 0 0 90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	E)
		echo "SETINSROTATION RBV 180 0 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	F)
		echo "SETINSROTATION RBV 180 0 90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	G)	
		echo "SETINSROTATION RBV 0 180 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	H)	
		echo "SETINSROTATION RBV 180 0 -90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	I)
		echo "SETINSROTATION RBV 0 -90 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	J)
		echo "SETINSROTATION RBV 90 -90 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	K)
		echo "SETINSROTATION RBV 0 90 180 " >> msg.txt
		nc $port_span < msg.txt
		;;
	L)
		echo "SETINSROTATION RBV -90 0 90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	M)
		echo "SETINSROTATION RBV 0 90 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	N)
		echo "SETINSROTATION RBV -90 0 -90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	O)
		echo "SETINSROTATION RBV 0 -90 180 " >> msg.txt
		nc $port_span < msg.txt
		;;
	P)
		echo "SETINSROTATION RBV 90 0 -90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	Q)
		echo "SETINSROTATION RBV -90 0 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	R)
		echo "SETINSROTATION RBV 0 -90 -90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	S)
		echo "SETINSROTATION RBV 180 0 180 " >> msg.txt
		nc $port_span < msg.txt
		;;
	T)
		echo "SETINSROTATION RBV 0 90 90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	U)
		echo "SETINSROTATION RBV 90 0 0 " >> msg.txt
		nc $port_span < msg.txt
		;;
	V)
		echo "SETINSROTATION RBV 0 90 -90 " >> msg.txt
		nc $port_span < msg.txt
		;;
	W)	
		echo "SETINSROTATION RBV -90 0 180 " >> msg.txt
		nc $port_span < msg.txt
		;;
	X)
		echo "SETINSROTATION RBV 0 -90 90 " >> msg.txt
		nc $port_span < msg.txt
		;;
 esac

 echo -e "\t\nSPAN rotations added\n\tCLOSING"
 echo -e "\n<<<<<<<<<<<<<<<<<<<<<<o>>>>>>>>>>>>>>>>>>>>>>>"

 exit 0
fi
