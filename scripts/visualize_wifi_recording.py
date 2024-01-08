#!/usr/bin/python3
import sys
from lib.dataset import Dataset, MergeFunction
from lib.visualize import show_plot_3d, show_plot_2d, Axis

# load the dataset at path (first command line argument)
filename = sys.argv[1]
# get the measurements related to the WiFi instrument
instrument = Dataset.load(filename).get_instrument("WiFi")
# filter values by value identifier (using regex) and supplying a function that decides
# how to merge multiple values that both match the regex
table = instrument.measurements_as_table(["Alstergym_WIFI", "CHANNEL:([1-9][2-9]|20)"], MergeFunction.max)
# table = instrument.measurements_as_table(["CHANNEL:([1-9][2-9]|20)"], MergeFunction.max)
# table = instrument.measurements_as_table(["SSID:Alstergym_WIFI"], MergeFunction.max)
# table = instrument.measurements_as_table(["^((?!Alstergym).)*$"], MergeFunction.max)
table = instrument.measurements_as_table(["MAC:86:25:19:8f:b6:86"], MergeFunction.max)

# print data as a csv (e.g., for use in Excel)
# print(table.csv())

# 3d or 2d visualization using matplotlib
# show_plot_3d(table)
show_plot_2d(table, Axis.Z)
