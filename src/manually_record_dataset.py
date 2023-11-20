#!/usr/bin/python3

import sys
import dataset
import uuid
import os
import subprocess

CSV_FILE = f"{uuid.uuid4()}.csv"


def get_signal_strength(ssid: str):
    """
    Windows
    """
    rows = str.split(subprocess.check_output("lswifi").decode("utf-8"), "\n")
    significant_rows = rows[3:]
    strongest = -1000
    for row in significant_rows:
        stripped = row.strip()
        split = str.split(stripped, " ")
        filtered = filter(lambda x : x != "", split)
        row_data = tuple(filtered)
        if (len(row_data) == 11) and (row_data[0] == ssid):
            dBm = int(row_data[2])
            if strongest < dBm:
                strongest = dBm
    return strongest

class ManRecorder():
    x: float = 0
    y: float = 0
    z: float = 0
    x_max: int
    y_max: int
    z_max: int

    def __init__(self, x_max, y_max, z_max):
        self.x_max = x_max
        self.y_max = y_max
        self.z_max = z_max

    def record(self):
        print("Enter \"s\" to skip to next column.")
        print("(near-far, left-right, floor-ceiling)")
        while True:
            print(f"({self.x}, {self.y}, {self.z}) = ", end="")
            value = get_signal_strength("")
            if value == "s":
                self.next_column()
                continue
            value = float(value)
            dataset.append_csv(CSV_FILE, self.x, self.y, self.z, value)
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
    print(get_signal_strength("Alstergym_WIFI"))
    sys.exit()
    if len(sys.argv) < 4:
        raise "Not enough arguments. You must provide x_max, y_max and z_max"
    mr = ManRecorder(*(int(x) for x in sys.argv[1:4]))
    mr.record()
