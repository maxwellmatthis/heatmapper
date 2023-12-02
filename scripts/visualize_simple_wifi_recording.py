#!/usr/bin/python3
from lib.dataset import Dataset
from lib.visualize import show_plot_3d, show_plot_2d, Axis

# data
filename = "simple-wifi-recording.json"
instrument = Dataset.load(filename).get_instrument("WiFi")
table = instrument.measurements_as_table()

print(table.csv())

# visualization
show_plot_3d(table, filename)
# show_plot_2d(table, Axis.Z, filename)
