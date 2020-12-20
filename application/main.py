import json
import os
import bluetooth._bluetooth as bluez
from datetime import datetime
import RPi.GPIO as GPIO
import time

from importlib.machinery import SourceFileLoader
ScanUtility = SourceFileLoader(
    "ScanUtility", '../scan/ScanUtility.py').load_module()


def init_Bluetooth(device: str):
    try:
        print("Bluetooth-Startup")
        os.system(f"sudo hciconfig {device} up")
        print("iBeacon-Setting")
        os.system(f"sudo hciconfig {device} noleadv")
    except:
        print("Init Bluetooth Failed")


def send_iBeacon(device: str, uuid: str, major: str, minor: str, power: str):
    try:
        os.system(
            f"sudo hcitool -i {device} cmd 0x08 0x0008 1e 02 01 1a 1a ff 4c 00 02 15 {uuid} {major} {minor} {power}")
        os.system(f"sudo hciconfig {device} leadv")
        print("iBeacon is working")
    except:
        print("Send iBeacon Error")


def switchMode(device: str):
    os.system(f"sudo hciconfig {device} noleadv")
    os.system(f"sudo hciconfig {device} piscan")


def main():
    with open('./config.json', 'r') as f:
        data = json.load(f)

    uuid = data['uuid']
    major = data['major']
    minor = data['minor']
    power = data['power']
    device = data['device']
    interval = data['interval']
    PIN = data['PIN']

    init_Bluetooth(device)
    send_iBeacon(device, uuid, major, minor, power)

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
    except:
        print("Can't find \"Vibration motor\"")
        PIN = -1

    try:
        sock = bluez.hci_open_dev(int(device[-1]))
        print("Open device sccuess")
    except:
        print("Error accessing bluetooth")
        return

    try:
        ScanUtility.hci_enable_le_scan(sock)
        record = open("record.txt", "a")
        print("\n *** Looking for BLE Beacons ***\n")
        print("\n *** CTRL-C to Cancel ***\n")
        while True:
            result = ScanUtility.parse_events(sock, 10)

            if result == "":
                continue

            distance = result['distance']

            if result['uuid'] == "07 48 52 36 d4 5a 6b 7c 55 32 12":
                record.close()
                print("Switch to connect phone")
                switchMode(device)
                return
            elif distance <= 2.0:
                if PIN >= 1 and distance <= 1.5:
                    GPIO.output(PIN, GPIO.HIGH)
                    print("Vibration")
                    time.sleep(2)
                    GPIO.output(PIN, GPIO.LOW)
                    time.sleep(1)
                current_time = datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
                custMajor = result['major']
                custMinor = result['minor']
                macAddress = result['macAddress']
                info = f"{current_time}/{macAddress}/{distance}/{custMajor}/{custMinor}\n"
                record.writelines(info)
                print("Write " + str(info))

    except KeyboardInterrupt:
        record.close()
        os.system(f"sudo hciconfig {device} noleadv")
        GPIO.cleanup()
        print("Stop Service")
        pass


if __name__ == "__main__":
    main()
