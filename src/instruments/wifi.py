#!/usr/bin/python3
import subprocess
from instruments.instrument import Instrument
from sys import platform


class WifiInstrument(Instrument):
    def __init__(self, ssid: str):
        self.ssid = ssid

    def get_signal_strength_linux(self) -> float:
        # todo
        return 0.0

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
