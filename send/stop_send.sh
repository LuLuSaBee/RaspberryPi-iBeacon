#!/bin/sh
. /home/pi/RaspberryPi-iBeacon/send/ibeacon.conf
echo "iBeacon-Disabling iBeacon"
sudo hciconfig $BLUETOOTH_DEVICE noleadv
echo "iBeacon -Stopped."
