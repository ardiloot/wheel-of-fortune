#!/bin/bash

echo "Monitoring pin state for poweroff signal..."
gpio mode 16 IN

while true
do
   VALUE=$(gpio read 16)
   if [[ $VALUE -eq 1 ]]
   then
    echo "Got poweroff signal..."
    sleep 5
    echo "Poweroff..."
    poweroff
    break
   fi
   sleep 2
done