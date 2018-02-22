#!/bin/bash



./Barrie-humidity.p &y
./Barrie-ozone.py &
./Barrie-temp.py &
./cpu_percent.py &
./cpu.py &
./memory_percent.py &
./memory.py &

echo " running all DATA sensors"
