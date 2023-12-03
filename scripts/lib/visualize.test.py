#!/usr/bin/python3
from lib.visualize import show_plot_3d, show_plot_2d, Axis
from lib.dataset import generate_random_dataset, MergeFunction, ValueType

ds1 = generate_random_dataset(500, 1)
ins1 = ds1.get_instrument("random_data")

show_plot_3d(ins1.measurements_as_table("."))

table = ins1.measurements_as_table()
show_plot_2d(table, Axis.Z)
show_plot_2d(table, Axis.X)
show_plot_2d(table, Axis.Y)

# The value function is based on Coulomb's law.
ds2 = generate_random_dataset(1000, 3, (lambda d: (
    1 / d**2) * 1000, ValueType("coulombly scaled", "C?", 3.5, 0)))
ds2.save()
ins2 = ds2.get_instrument("random_data")

print(ins2.measurements_as_table().csv()[:2000])
show_plot_3d(ins2.measurements_as_table())
show_plot_3d(ins2.measurements_as_table(".", MergeFunction.lesser))
show_plot_3d(ins2.measurements_as_table("e1"))
show_plot_3d(ins2.measurements_as_table("e2"))
show_plot_3d(ins2.measurements_as_table("e1|e2", MergeFunction.accumulate))
