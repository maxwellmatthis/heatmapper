#!/usr/bin/python3
import sys
from lib.dataset import Dataset
from lib.visualize import show_plot_2d, Axis

filename = sys.argv[1]
ds = Dataset.load(filename)
instrument = ds.get_instrument("WiFi")

for m in instrument.measurements:
    # m.coordinates.y = 2 * m.coordinates.y
    # m.coordinates.x = 2 * m.coordinates.x
    # m.coordinates.z = 1.5
    pass

show_plot_2d(instrument.measurements_as_table(), Axis.Z)

# Make sure that you have mutated your data correctly before overwriting the file.
# ds.save()
