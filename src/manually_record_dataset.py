#!/usr/bin/python3

import sys
import dataset
import uuid

CSV_FILE = f"{uuid.uuid4()}.csv"

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
            value = input(f"({self.x}, {self.y}, {self.z}) = ")
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
    if len(sys.argv) < 4:
        raise "Not enough arguments. You must provide x_max, y_max and z_max"
    mr = ManRecorder(*(int(x) for x in sys.argv[1:4]))
    mr.record()
