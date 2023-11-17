# Heatmapper

Software for recording, analyzing and visualizing three-dimensional heat maps.

## Setup

Make sure to run `pip install -r requirements.txt` to install all necessary dependencies.

## Usage

### Visualize measurements in a CSV file

Directly from python code:

```python
import src.visualize as vis

# in 3D space
vis.show_plot_3d(dataset, best_possible_value, worst_possible_value)

# flattened to 2D by ignoring one axis
vis.show_plot_2d(dataset, best_possible_value, worst_possible_value, "y")
```

From the command line:

```sh
./src/visualize.py <path/to/dataset.csv> ["3d" | "2d", default="3d"] [best-possible-value, default=1.0] [worst-possible-value, default=0.0] [(2d-only) axis, options="x", "y", "z", default="y"]
```

### Working with datasets

Directly from python code:

```python
import src.dataset as dat

# read CSV
dat.read_csv("/path/to/file.csv")

# write CSV
dat.write_csv("/path/to/file.csv", dataset)

# generate random dataset
dat.generate_random_dataset(area_width, area_height, area_depth, area_number_of_measurement_points, number_of_emitters)
```

From the command line:

```sh
./src/dataset.py [path/of/new-random-dataset.csv, default=test-dataset.csv] [area-width, default=100.0] [area-height, default=100.0] [area-width, default=100.0] [measurement-count, default=1000] [emitter-count, default=2]
```

### Getting relative positions using the object tracker

Just run the script. To set the program up for your own camera, tweak the global constants at the beginning of the script.

### Semi-manually create a CSV with values

```sh
./src/manually_record_dataset.py <x_max> <y_max> <z_max>
```

## Examples

See [src/dataset.test.py](src/dataset.test.py) and [src/visualize.test.py](src/visualize.test.py) for some examples of how to use the helpers.
