import threading
import json
import os
import bluetooth._bluetooth as bluez
from datetime import datetime

from importlib.machinery import SourceFileLoader
ScanUtility = SourceFileLoader(
    "ScanUtility", '../scan/ScanUtility.py').load_module()


def send_iBeacon(device: str, uuid: str, major: str, minor: str, power: str):
    try:
        print("Bluetooth-Startup")
        os.system(f"sudo hciconfig {device} up")
        print("iBeacon-Setting")
        os.system(f"sudo hciconfig {device} noleadv")
        os.system(
            f"sudo hcitool -i {device} cmd 0x08 0x0008 1e 02 01 1a 1a ff 4c 00 02 15 {uuid} {major} {minor} {power}")
        os.system(f"sudo hciconfig {device} leadv 0")
        print("iBeacon is working")
    except:
        print("send iBeacon Error")


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

    timer = threading.Timer(interval=interval, function=send_iBeacon(
        device, uuid, major, minor, power))

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
            print(result)

            if result['uuid'] == "07":
                record.close()
                timer.cancel()
                print("Switch to connect phone")
                switchMode(device)
                return
            elif result['distance'] <= 2.0:
                current_time = datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
                custMajor = result['major']
                custMinor = result['minor']
                distance = result['distance']
                macAddress = result['macAddress']
                info = f"{current_time}/{macAddress}/{distance}/{custMajor}/{custMinor}"
                record.writelines(info)
                print("Write into")

    except KeyboardInterrupt:
        record.close()
        timer.cancel()
        os.system(f"sudo hciconfig {device} noleadv")
        print("Stop Service")
        pass


if __name__ == "__main__":
    main()
