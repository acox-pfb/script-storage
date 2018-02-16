#!/bin/bash

#This will add a random value into paddedHGR so it can be plotted.
datasets="/home/acox/Documents/LinktoDocs/2_work/Injection-testing/datasets/plots"
cd $datasets
for f in 40; do sed -i "s/^/$f\t/" paddedHGRData.csv; done
