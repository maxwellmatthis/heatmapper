#!/usr/bin/python3

import sys
from processing import dataset
from instruments.instrument import Instrument
from instruments.wifi import WifiInstrument


class GridRecorder:
    x: float = 0
    y: float = 0
    z: float = 0
    x_max: int
    y_max: int
    z_max: int

    def __init__(self, instrument: Instrument, filename: str, x_max: int, y_max: int, z_max: int):
        self.instrument = instrument
        self.filename = filename
        self.x_max = x_max
        self.y_max = y_max
        self.z_max = z_max

    def save_value(self, value: float) -> str:
        return dataset.append_csv(self.filename, self.x, self.y, self.z, value)

    def record(self):
        print("Press <enter> to take the measurement and <s> to skip to next cube.")
        print("Format: x (near-far), y (left-right), z (floor-ceiling) = <value>")
        while True:
            print(
                f"Waiting to take measurement at ({self.x}, {self.y}, {self.z})...", end="")
            value = 0.0
            if input() == "s":
                value = "skipped"
            else:
                value = self.instrument.measure()
                if value is None:
                    print("Failed to take measurement.")
                    value = "failed"

            uuid = self.save_value(value)
            print(f"=> {value} ({uuid})")
            if not self.next_shelf():
                break

    def next_shelf(self):
        self.z += 1
        if self.z == self.z_max:
            return self.next_column()
        return True

    def next_column(self):
        self.y += 1
        self.z = 0
        if self.y == self.y_max:
            return self.next_slice()
        return True

    def next_slice(self):
        self.x += 1
        self.y = 0
        if self.x == self.x_max:
            return False
        return True


if __name__ == "__main__":
    if len(sys.argv) < 6:
        raise Exception("Usage: <path/to/output.csv> <x_max> <y_max> <z_max> <WiFi SSID>")

    # grid recorder specific arguments
    filename = sys.argv[1]
    bounds = sys.argv[2:5]

    # wifi specific
    ssid = sys.argv[5]
    selected_instrument = WifiInstrument(ssid)

    mr = GridRecorder(selected_instrument, filename, *(int(x) for x in bounds))
    mr.record()
