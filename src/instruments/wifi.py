#!/usr/bin/python3
import subprocess
from instruments.instrument import Instrument
from sys import platform
import re
import os

def is_running_as_root() -> bool:
    return os.geteuid() == 0

class WifiInstrument(Instrument):
    def __init__(self, ssid: str):
        self.ssid = ssid

    def get_signal_strength_linux(self) -> float:
        if not is_running_as_root():
            print("WARNING: YOU MUST BE ROOT TO INTIATE A NETWORK SCAN. OTHERWISE THE INFORMATION WILL BE FROM THE LAST AUTOMATIC SCAN, WHICH COULD BE MINUTES AGO.")
        rows = subprocess.run([f"iwlist", "wlan0", "scanning"], check=True, capture_output=True, text=True).stdout
        rows = str.split(rows, "\n")
        rows = list(filter(lambda x : "SSID" in x or "Signal" in x, rows))
        strongest = -1000
        for pair_index in range(int(len(rows) / 2)):
            signal_line = rows[2 * pair_index].strip()
            rssi = re.search("-\d+", signal_line).group()
            rssi = float(rssi)
            ssid_line = rows[2 * pair_index + 1].strip()
            ssid = re.sub("ESSID:\"", "", ssid_line)[:-1]
            if ssid == self.ssid:
                if strongest < rssi:
                    strongest = rssi
        return float(strongest)

    def get_signal_strength_macos(self) -> float:
        rows = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s", self.ssid], check=True, capture_output=True, text=True).stdout
        rows = str.split(rows, "\n")
        start_of_rssi_column = rows[0].find("RSSI")
        best_rssi = -1000
        significant_rows = rows[1:]
        significant_rows = filter(lambda x : x != "", significant_rows)
        for row in significant_rows:
            rssi = float(row[start_of_rssi_column:start_of_rssi_column+4].strip())
            if rssi > best_rssi:
                best_rssi = rssi
        return best_rssi

    def get_signal_strength_windows(self) -> float:
        rows = str.split(subprocess.check_output(
            "lswifi").decode("utf-8"), "\n")
        significant_rows = rows[3:]
        strongest = -1000
        for row in significant_rows:
            stripped = row.strip()
            split = str.split(stripped, " ")
            filtered = filter(lambda x: x != "", split)
            row_data = tuple(filtered)
            if (len(row_data) == 11) and (row_data[0] == self.ssid):
                dBm = int(row_data[2])
                if strongest < dBm:
                    strongest = dBm
        return float(strongest)

    def measure(self) -> float:
        if platform == "linux" or platform == "linux2":
            return self.get_signal_strength_linux()
        elif platform == "darwin":
            return self.get_signal_strength_macos()
        elif platform == "win32":
            return self.get_signal_strength_windows()
        else:
            raise Exception(f"Invalid platform: {platform}")
