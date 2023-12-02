#!/usr/bin/python3
from lib.dataset import Dataset, Coordinates
from lib.instruments.wifi import WifiInstrument, NoScanDataException


if __name__ == "__main__":
    INS = WifiInstrument("wlan0")
    DS = Dataset("Simple WiFi Recording").add_instrument(INS)
    DS.enable_save_on_terminate()

    i = 0
    while True:
        note = input(
            "Waiting for <enter> to take next measurement. Enter a note for the next measurement here: ")
        try:
            measurement = INS.take_measurement(Coordinates(i, 0, 0), note)
            print(measurement)
            i += 1
        except NoScanDataException:
            print("The scan command did not yield any output.")
