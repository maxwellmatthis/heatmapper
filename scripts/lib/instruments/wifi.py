#!/usr/bin/python3
from typing import *
from sys import platform
import os
import subprocess
import re
from lib.dataset import Instrument, Value, Values, ValueType


# RSSI = Received Signal Strength Indicator
RSSI = ValueType("RSSI", "dBm", -30, -80)


class NoScanDataException(Exception):
    pass


def posix_is_root():
    return os.geteuid() == 0


def prepare_get_access_points_linux(interface: str):
    def get_access_points_linux() -> Values:
        cmd = [f"iwlist", interface, "scanning" if posix_is_root() else "scan"]
        rows = subprocess.run(
            cmd, check=True, capture_output=True, text=True).stdout
        rows = str.split(rows, "\n")
        rows = [row for row in rows
                if "SSID" in row
                or "Signal level" in row
                or "Address" in row
                or "Frequency" in row]
        """
        # Example Command Output After Filtering Rows
        ```sh
                  Cell 01 - Address: AB:12:34:56:78:CD
                            Frequency:2.412 GHz (Channel 1)
                            Quality=52/70  Signal level=-58 dBm
                            ESSID:"My Network 123"
                  Cell 02 - Address: EF:CD:78:56:34:12
                            Frequency:5.18 GHz (Channel 36)
                            Quality=46/70  Signal level=-64 dBm
                            ESSID:"Other Network" 
        ```
        """
        ROWS_PER_CELL = 4  # since we are looking for 4 values

        APs = {}
        for quad_index in range(int(len(rows) / ROWS_PER_CELL)):
            quad_base_index = ROWS_PER_CELL * quad_index

            address_line = rows[quad_base_index].strip()
            address = address_line.split(" ")[-1]

            frequency_line = rows[quad_base_index + 1].strip()
            frequency = re.search(
                "\d.\d+ GHz", frequency_line).group().replace(" GHz", "")
            channel = re.search(
                "Channel .+", frequency_line).group().replace("Channel ", "")

            signal_line = rows[quad_base_index + 2].strip()
            rssi = re.search("-\d+", signal_line).group()
            rssi = float(rssi)

            ssid_line = rows[quad_base_index + 3].strip()
            ssid = re.sub("ESSID:\"", "", ssid_line)[:-1]

            ap_identifier = f"SSID:{ssid};MAC:{address};FREQUENCY:{frequency};CHANNEL:{channel}"

            APs[ap_identifier] = Value(RSSI, rssi)

        return APs
    return get_access_points_linux


def prepare_get_access_points_macos(interface: str):
    # TODO: migrate to new API and use interface?
    def get_access_points_macos() -> Values:
        cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"]
        """
        # Example Command Output
        ```sh
                          SSID BSSID             RSSI CHANNEL HT CC SECURITY (auth/unicast/group)
                My Network 123 ab:12:34:56:78:cd -88  36,+1   Y  -- RSN(802.1x/AES/AES)
                 Other Network ef:cd:78:56:34:12 -75  1       Y  -- RSN(PSK/AES/AES)
        ```
        """
        rows = subprocess.run(
            cmd, check=True, capture_output=True, text=True).stdout
        if rows.strip() == "":
            raise NoScanDataException
        rows = str.split(rows, "\n")
        rows = [row for row in rows if row.strip() != ""]
        if len(rows) < 2:
            raise NoScanDataException

        end_of_ssid_column = rows[0].find(" SSID ") + 1 + 4  # network name
        start_of_bssid_column = rows[0].find(" BSSID ") + 1  # AP MAC
        start_of_channel_column = rows[0].find(" CHANNEL ") + 1  # subfrequency
        start_of_ht_column = rows[0].find(" HT ") + 1
        start_of_security_column = rows[0].find(" SECURITY ") + 1
        start_of_rssi_column = rows[0].find(" RSSI ") + 1

        APs: Values = {}
        for row in rows[1:]:
            ssid = row[:end_of_ssid_column].strip()
            bssid = row[start_of_bssid_column:start_of_rssi_column].strip()
            channel = row[start_of_channel_column:start_of_ht_column].strip()
            security = row[start_of_security_column:].strip()
            ap_identifier = f"SSID:{ssid};" + (f"MAC:{bssid};" if posix_is_root(
            ) else "") + f"CHANNEL:{channel};SECURITY:{security}"

            rssi = row[start_of_rssi_column:start_of_rssi_column+4].strip()
            rssi = float(rssi)

            APs[ap_identifier] = Value(RSSI, rssi)

        return APs
    return get_access_points_macos


def prepare_get_access_points_windows(interface: str):
    # TODO: update windows function for new format and check if interface can be parameterized
    def get_access_points_windows() -> Values:
        rows = str.split(subprocess.check_output(
            "lswifi").decode("utf-8"), "\n")
        significant_rows = rows[3:]
        strongest = -1000
        for row in significant_rows:
            stripped = row.strip()
            split = str.split(stripped, " ")
            filtered = filter(lambda x: x != "", split)
            row_data = tuple(filtered)
            if (len(row_data) == 11):
                dBm = int(row_data[2])

        return {}
    return get_access_points_windows


class WifiInstrument(Instrument):
    def __init__(self, interface: Optional[str]):
        """
        Set interface to `None` to use the default interface.
        """
        do_measure_function = None
        if platform == "linux" or platform == "linux2":
            if not posix_is_root():
                print("WARNING: YOU MUST BE ROOT TO INTIATE A NEW NETWORK SCAN. THE DATA PROVIDED TO NON-SUPERUSERS MAY BE A FEW MINUTES OLD.")
            if interface is None:
                interface = "wlan0"
            do_measure_function = prepare_get_access_points_linux(interface)
        elif platform == "darwin":
            if not posix_is_root():
                print(
                    "WARNING: YOU MUST BE ROOT TO ACCESS CERTAIN INFORMATION SUCH AS THE BSSID (MAC) OF AN ACCESS POINT.")
            if interface is None:
                interface = "en0"
            do_measure_function = prepare_get_access_points_macos(interface)
        elif platform == "win32":
            do_measure_function = prepare_get_access_points_windows(interface)
        else:
            raise Exception(f"Invalid platform: {platform}")
        super().__init__("WiFi", {"platform": platform, "interface": interface}, [
            RSSI], do_measure_function)
