# Heatmapper

Software for recording, analyzing and visualizing data as three-dimensional heat maps.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Usage (by Example)](#usage-by-example)
    - [Taking Measurements](#taking-measurements)
    - [Visualizing Measurements](#visualizing-measurements)
- [Component Overview](#component-overview)
    - [Measurements](#measurements)
    - [Instruments](#instruments)
        - [Supported Instruments](#supported-instruments)
    - [Datasets](#datasets)

## Installation & Setup

1. Make sure to run `python3 -m pip install -r requirements.txt` to install all necessary
dependencies.

2. Set the `PYTHONPATH` environment variable to the absolute location of the `scripts` directory.
This step ensures that all the modules are available, even when you run a script not located in
the `scripts` directory.

__Tip:__ If you're looking to for more customization options, try tuning the global constants in
the script you're dealing with.

## Usage (by Example)

### Taking Measurements

__Note:__ The following script assumes that measurements are made every meter in a straight line
along the x-axis. This is likely not going to be how you measure WiFi in reality. If you are
taking or took the measurements in a pattern of known dimensions, you could easily write a script
that calculates or updates the coordinates. Automatically keeping track of arbitrary measurement
points can get very complicated. Relatively easy and reliable solutions include GPS and optical
tracking.

```python
# from: scripts/simple_wifi_recorder.py

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
```

### Visualizing Measurements

```python
# from: scripts/visualize_wifi_recording.py

import sys
from lib.dataset import Dataset, MergeFunction
from lib.visualize import show_plot_3d, show_plot_2d, Axis

# load the dataset at path (first command line argument)
filename = sys.argv[1]
# get the measurements related to the WiFi instrument
instrument = Dataset.load(filename).get_instrument("WiFi")
# filter values by value identifier (using regex) and supplying a function that decides
# how to merge multiple values that both match the regex
table = instrument.measurements_as_table(["."], MergeFunction.greater)

# print data as a csv (e.g., for use in Excel)
print(table.csv())

# 3d or 2d visualization using matplotlib
show_plot_3d(table, filename)
show_plot_2d(table, Axis.Z, filename)
```

The following image shows what the 2D WiFi heat map of a large building could look like. Here we are using a regular expression to filter for wifi access points transmitting on the 5GHz frequency band.

<img width="972" alt="Screenshot 2023-12-28 at 10 18 27 PM" src="https://github.com/maxwellmatthis/heatmapper/assets/58150536/3c3acf61-cb7c-4184-befc-ec48aefe677c">

## Component Overview

### Measurements

Creating a spacial heat map requires having lots of data points or measurements.

Each measurement includes

- a set of three-dimensional coordinates,
- an ID,
- an optional note about the measurement,
- and a dictionary of values, consisting of a type and a numeric value.

### Instruments

Each type of measurement requires an "instrument", e.g., a thermometer or WiFi card.
Each instrument requires a driving script that provides a custom implementation of
`lib.dataset.Instrument` to help take and store measurements and metadata.

The driving scripts are located in the [instruments directory](./scripts/lib/instruments/).

#### Supported Instruments

| Name | Data Measured | Requirements |
| ---- | ------------- | ------------ |
| WiFi | WiFi signal strength by access point and channel in dBm | WiFi-capable computer running Windows, Linux or MacOS |

### Datasets

Datasets contain one or more instruments along with a bit of general metadata.
The [dataset.py](./scripts/lib/dataset.py) script provides useful classes and methods for creating,
saving, reading and understanding datasets and the instruments and measurements within.

When run directly the script creates a test dataset:

```sh
python3 ./scripts/lib/dataset.py
```
