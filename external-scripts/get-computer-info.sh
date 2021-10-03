#!/bin/bash

# To run the script at start-up, follow these steps:
#  1. Run "crontab -e"
#  2. Add this line "@reboot ./get-computer-info.sh utility rpiNfs &"
#  3. Run "sudo reboot -h now"

MQTT_IP=192.168.0.204
MQTT_PORT=1883

print_usage() {
	echo "Usage: get_computer_info location name"
}

if [[ ! -n $1 ]]; then
	echo "Must provide the computer location."
	print_usage
	exit 1
fi

if [[ ! -n $2 ]]; then
	echo "Must provide the computer name."
	print_usage
	exit 1
fi

CPU_TEMPERATURE_CHANNEL="computer/$1/$2/cpuTemperature"
GPU_FAN_CHANNEL="computer/$1/$2/gfxFanSpeed"
GPU_TEMPERATURE_CHANNEL="computer/$1/$2/gfxTemperature"
LAST_UPDATED_CHANNEL="computer/$1/$2/updatedTimestamp"

if [[ `uname -m` == "armv7l" ]]; then
	PLATFORM="RaspberryPi"
else
	PLATFORM="Windows"
fi

while :
do
	if [[ $PLATFORM == "Windows" ]]; then
		gpu_fan_speed=`nvidia-smi -q | grep -E "Fan.*([[:digit:]]+) %" | awk '{print $4}'`
		gpu_temperature=`nvidia-smi -q | grep "GPU Current Temp" | awk '{print $5}'`
	elif [[ $PLATFORM == "RaspberryPi" ]]; then
 		# PI's temperature has to be divided by 1_000 to get the degree.
		large_value=`cat /sys/class/thermal/thermal_zone0/temp`
		cpu_temperature=$((large_value / 1000))

		gpu_temperature=`vcgencmd measure_temp | grep -P "\d+(\.\d+)*" -o`
	else
		echo "Unknown platform $PLATFORM"
		exit 1
	fi

	if [[ -v cpu_temperature ]]; then
		mosquitto_pub -h $MQTT_IP -p $MQTT_PORT -t $CPU_TEMPERATURE_CHANNEL -m $cpu_temperature
		echo "Sent $cpu_temperature to $CPU_TEMPERATURE_CHANNEL"
	fi

	if [[ -v gpu_fan_speed ]]; then
		mosquitto_pub -h $MQTT_IP -p $MQTT_PORT -t $GPU_FAN_CHANNEL -m $gpu_fan_speed
		echo "Sent $gpu_fan_speed to $GPU_FAN_CHANNEL"
	fi

	if [[ -v gpu_temperature ]]; then
		mosquitto_pub -h $MQTT_IP -p $MQTT_PORT -t $GPU_TEMPERATURE_CHANNEL -m $gpu_temperature
		echo "Sent $gpu_temperature to $GPU_TEMPERATURE_CHANNEL"
	fi

    mosquitto_pub -h $MQTT_IP -p $MQTT_PORT -t $LAST_UPDATED_CHANNEL -m `date --iso-8601=seconds`

    sleep 60s
done
