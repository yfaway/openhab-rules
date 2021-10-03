# MIT License
#
# Copyright (c) 2018 Airthings AS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://airthings.com

# Additional modification to retrieve only the radon gas value, temperature and
# humidty every 5 minutes. These values are then sent to the following MQTT
# topics:
#   - airthings/utility/radonGas/value
#   - airthings/utility/radonGas/state  (if the value crosses a threshold)
#   - airthings/utility/temperature/value
#   - airthings/utility/humidity/value
#
# To run the script at start-up, follow these steps:                                                
#  1. Run "crontab -e"                                                                              
#  2. Add this line "@reboot python2 read_wave.py b0:91:22:75:e1:48 &"                               
#  3. Run "sudo reboot -h now"

from bluepy.btle import UUID, Peripheral
from datetime import datetime
import sys
import time
import struct
import re
import subprocess
import time

MQTT_IP = "192.168.0.204"
MQTT_PORT = "1883"
MQTT_CHANNEL_PREFIX = "airthings/utility/"
RADON_UPPER_THRESHOLD = 30

class Sensor:
    def __init__(self, name, uuid, format_type, unit, scale):
        self.name = name
        self.uuid = uuid
        self.format_type = format_type
        self.unit = unit
        self.scale = scale

def send_mqtt_message(channel, message):
    subprocess.call(['mosquitto_pub', '-h', MQTT_IP, '-p', MQTT_PORT, '-t', channel, '-m', message])

if len(sys.argv) != 2:
    print("USAGE: read_wave.py \"MAC\"\n where MAC is the address of the Wave and on the format AA:BB:CC:DD:EE:FF")
    sys.exit(1)

if not re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", sys.argv[1].lower()):
    print("USAGE: read_wave.py \"MAC\"\n where MAC is the address of the Wave and on the format AA:BB:CC:DD:EE:FF")
    sys.exit(1)

time.sleep(60) # wait till the bluetooth stack is ready after reboot

try:
    sensors = []
    #sensors.append(Sensor("DateTime", UUID(0x2A08), 'HBBBBB', "\t", 0))
    sensors.append(Sensor("Temperature", UUID(0x2A6E), 'h', "deg C\t", 1.0/100.0))
    sensors.append(Sensor("Humidity", UUID(0x2A6F), 'H', "%\t\t", 1.0/100.0))
    sensors.append(Sensor("Radon 24h avg", "b42e01aa-ade7-11e4-89d3-123b93f75cba", 'H', "Bq/m3\t", 1.0))
    #sensors.append(Sensor("Radon long term", "b42e0a4c-ade7-11e4-89d3-123b93f75cba", 'H', "Bq/m3\t", 1.0))

    p = Peripheral()

    while 1:
        p.connect(sys.argv[1])
        # Get and print sensor data
        str_out = ""
        for s in sensors:
            ch  = p.getCharacteristics(uuid=s.uuid)[0]
            if (ch.supportsRead()):
                val = ch.read()
                val_array = struct.unpack(s.format_type, val)

                value = val_array[0] * s.scale
                str_value = str(value)
                str_out += str_value + " "

                if s.name == "Radon 24h avg":
                    send_mqtt_message(MQTT_CHANNEL_PREFIX + "radonGas/value", str_value)

                    if value >= RADON_UPPER_THRESHOLD:
                        send_mqtt_message(MQTT_CHANNEL_PREFIX + "radonGas/state", "1")
                    else:
                        send_mqtt_message(MQTT_CHANNEL_PREFIX + "radonGas/state", "0")
                elif s.name == "Temperature":
                    send_mqtt_message(MQTT_CHANNEL_PREFIX + "temperature/value", str_value)
                elif s.name == "Humidity":
                    send_mqtt_message(MQTT_CHANNEL_PREFIX + "humidity/value", str_value)

        print(str_out)
        p.disconnect()

        time.sleep(5 * 60)
finally:
    pass
