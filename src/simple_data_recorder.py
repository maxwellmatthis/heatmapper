#!/usr/bin/python3

import sys
import time
from processing import dataset
from instruments.wifi import WifiInstrument


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception("Usage: <\"time\" | \"keypress\"> <path/to/output.csv> <WiFi SSID>")
    mode = sys.argv[1]
    filepath = sys.argv[2]
    ssid = sys.argv[3]

    INSTRUMENT = WifiInstrument(ssid)
    while True:
        if mode == "time":
            time.sleep(1)
        else:
            input("Waiting for <enter> to take next measurement.")
        value = INSTRUMENT.measure()
        dataset.append_csv(filepath, 0, 0, 0, value)
        print(value)
