# Heatmapper

Software for recording, analyzing and visualizing data as three-dimensional heat maps.

## Installation & Setup

Make sure to run `python3 -m pip install -r requirements.txt` to install all necessary dependencies.

__Note:__ Some scripts require changing hard-coded constants or a bit of logic in
the `if __name__ == "__main__"` part of the script. Check there if things are not working
as expected or if you're missing a customization option in the CLI.

## Working with Datasets

Script: [dataset.py](./src/processing/dataset.py)

Directly from python code:

```python
import src.dataset as dat

# read CSV
dat.read_csv("/path/to/file.csv")

# write CSV
dat.write_csv("/path/to/file.csv", dataset)

# append CSV entry
entry_uuid = dat.append_csv("/path/to/file.csv", x, y, z, value)

# generate random dataset
dat.generate_random_dataset(area_width, area_height, area_depth, area_number_of_measurement_points, number_of_emitters)
```

From the command line:

```sh
python3 ./src/dataset.py [path/of/new-random-dataset.csv, default=test-dataset.csv] [area-width, default=100.0] [area-height, default=100.0] [area-width, default=100.0] [measurement-count, default=1000] [emitter-count, default=2]
```

## Visualizing Datasets

Script: [visualize.py](./src/processing/visualize.py)

Directly from python code:

```python
import src.visualize as vis

# in 3D space
vis.show_plot_3d(dataset, best_possible_value, worst_possible_value)

# flattened to 2D by ignoring one axis
vis.show_plot_2d(dataset, "z", best_possible_value, worst_possible_value)
```

From the command line:

```sh
python3 ./processing/visualize.py <path/to/dataset.csv> ["3d" | "2d", default="3d"] [(2d-only) axis, options="x", "y", "z", default="z"] [best-possible-value, default=1.0] [worst-possible-value, default=0.0]
```

<img width="712" alt="Screenshot 2023-11-21 at 9 30 36 PM" src="https://github.com/maxwellmatthis/heatmapper/assets/58150536/4363b28a-371f-4018-add9-9660f1f83809">

## Recording Measurements by Manually Measuring a 3d-Grid

Script: [grid_recorder.py](./src/grid_recorder.py)

```sh
python3 ./src/grid_recorder.py <path/to/output.csv> <x_max> <y_max> <z_max> <WiFi SSID>
```

__About:__ This script helps take measurements in a space with the dimensions
`x_max * y_max * z_max` by telling the user where to stand when
the measurement is taken.

## Recording Measurements Independently of Position Data

Script: [simple_data_recorder.py](./src/simple_data_recorder.py)

```sh
python3 ./simple_data_recorder.py <"time" | "keypress"> <path/to/output.csv> <WiFi SSID>
```

__About:__ This script takes a measurement every second or when the enter key
is pressed, depending on the mode.

__Tip:__ Use this script alongside a position recorder to supply position data
for the recorded measurements.

## Recording Position Data Using the Mono Optical Object Tracker

Script: [mono_optical_position_recorder.py](./src/mono_optical_position_recorder.py)

```sh
python3 ./src/mono_optical_position_recorder.py
```

__About:__ This script helps take measurements by determining the position of the
measurement by taking a picture and calculating the relative position
of my orange pasta colander (or any orange circle with a diameter of 25cm).

__Customizing:__ To set the program up to work with your own camera, tweak the
global constants at the beginning of the script.

__Tip:__ Use this script alongside a simple data recorder to supply measurement data
for the recorded positions.

## Measurement Instruments

Each type of measurement requires an "instrument". The driving scripts for supported instruments are located in the [instruments folder](./src/instruments/).

### Supported Instruments

| Name | Data Measured | Requirements |
| ---- | ------------- | ------------ |
| WiFi | WiFi signal strength by SSID in dBm | WiFi-capable computer running Windows, Linux or MacOS |
