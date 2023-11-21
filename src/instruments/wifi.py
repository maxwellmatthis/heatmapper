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
        # todo
        return 0.0

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
