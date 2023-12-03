#!/usr/bin/python3
from lib.dataset import Dataset, MergeFunction
from lib.visualize import show_plot_3d, show_plot_2d, Axis

# load the "simple-wifi-recording.json" dataset
filename = "simple-wifi-recording.json"
# get the measurements related to the WiFi instrument
instrument = Dataset.load(filename).get_instrument("WiFi")
# filter values by value identifier (using regex) and supplying a function that decides
# how to merge multiple values that both match the regex
table = instrument.measurements_as_table(".", MergeFunction.greater)

# print data as a csv (e.g., for use in Excel)
print(table.csv())

# 3d or 2d visualization using matplotlib
show_plot_3d(table, filename)
show_plot_2d(table, Axis.Z, filename)
