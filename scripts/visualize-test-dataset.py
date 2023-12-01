#!/usr/bin/python3
from lib.dataset import Dataset
from lib.visualize import show_plot_3d, show_plot_2d, Axis

# data
filename = "random-test-dataset.json"
instrument = Dataset.load(filename).get_instrument("random_data")
table = instrument.measurements_as_table()

# visualization
show_plot_3d(table, filename)
show_plot_2d(table, Axis.Z, filename)
