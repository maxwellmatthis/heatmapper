#!/usr/bin/python3

import visualize
import dataset

ds1 = dataset.generate_random_dataset(100, 100, 100, 1000, 1)

visualize.show_plot_3d(ds1, 0, 100)
visualize.show_plot_2d(ds1, 0, 100, "y")
visualize.show_plot_2d(ds1, 0, 100, "z")
visualize.show_plot_2d(ds1, 0, 100, "x")

# The value function is based on Coulomb's law.
ds2 = dataset.generate_random_dataset(100, 100, 100, 1000, 2, lambda d: (1 / d**2) * 1000)

visualize.show_plot_3d(ds2)
