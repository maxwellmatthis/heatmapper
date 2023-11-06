#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib
import dataset


DEFAULT_BEST_POSSIBLE_VALUE = 1.0
DEFAULT_WORST_POSSIBLE_VALUE = 0.0


def show_plot_3d(
    dataset: dataset.DATASET_TYPE,
    best_possible_value: float = DEFAULT_BEST_POSSIBLE_VALUE,
    worst_possible_value: float = DEFAULT_WORST_POSSIBLE_VALUE
):
    """
    Displays a dataset in 3D space using matplotlib.

    The points will be colored based on the best and worst possible values.
    Green is the best, yellow is medium, and red ist the worst.

    Note: The `best_possible_value` does not have to be greater than the `worst_possible_value`.
    The function will automatically adapt to display the values correctly. 
    """
    # graph
    x_vals, y_vals, z_vals, values, _ids = zip(*dataset)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection='3d')

    # color
    cm = None
    cNorm = None
    if best_possible_value >= worst_possible_value:
        # higher-is-better mode
        cm = plt.get_cmap('Spectral')
        cNorm = matplotlib.colors.Normalize(
            vmin=worst_possible_value, vmax=best_possible_value)
    else:
        # lower-is-better mode
        cm = plt.get_cmap('Spectral_r')
        cNorm = matplotlib.colors.Normalize(
            vmin=best_possible_value, vmax=worst_possible_value)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

    # display
    ax.scatter(x_vals, y_vals, z_vals, c=scalarMap.to_rgba(values))
    plt.show()


DEFAULT_FLATTENING_AXIS = "y"


def show_plot_2d(
    dataset: dataset.DATASET_TYPE,
    best_possible_value: float = DEFAULT_BEST_POSSIBLE_VALUE,
    worst_possible_value: float = DEFAULT_WORST_POSSIBLE_VALUE,
    ignore_axis: str = DEFAULT_FLATTENING_AXIS
):
    """
    Displays a dataset in 2D space using matplotlib.
    Flattening the y-axis gives a top down view; 
    flattening the x-axis gives a left to right view; 
    flattening the z-axis gives a straight-on view.

    The points will be colored based on the best and worst possible values.
    Green is the best, yellow is medium, and red ist the worst.

    Note: The `best_possible_value` does not have to be greater than the `worst_possible_value`.
    The function will automatically adapt to display the values correctly.
    """
    # graph
    x_vals, y_vals, z_vals, values = zip(*dataset)
    # default: flatten floor to ceiling
    xy2d = [x_vals, z_vals]
    if ignore_axis == "x":
        # flatten left to right
        xy2d = [y_vals, z_vals]
    elif ignore_axis == "z":
        # flatten near to far
        xy2d = [x_vals, y_vals]
    ax = plt.subplot()

    # color
    cm = None
    cNorm = None
    if best_possible_value >= worst_possible_value:
        # higher-is-better mode
        cm = plt.get_cmap('Spectral')
        cNorm = matplotlib.colors.Normalize(
            vmin=worst_possible_value, vmax=best_possible_value)
    else:
        # lower-is-better mode
        cm = plt.get_cmap('Spectral_r')
        cNorm = matplotlib.colors.Normalize(
            vmin=best_possible_value, vmax=worst_possible_value)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

    # display
    ax.scatter(*xy2d, c=scalarMap.to_rgba(values))
    plt.show()


def print_usage():
    print(
        f"Usage: {sys.argv[0]} "
        + "<path/to/dataset.csv> "
        + "[\"3d\" | \"2d\", default=\"3d\"] "
        + f"[best-possible-value, default={DEFAULT_BEST_POSSIBLE_VALUE}] "
        + f"[worst-possible-value, default={DEFAULT_WORST_POSSIBLE_VALUE}] "
        + f"[(2d-only) axis, options=\"x\", \"y\", \"z\", default=\"{DEFAULT_FLATTENING_AXIS}\"]"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
    else:
        if (len(sys.argv) > 2 and sys.argv[2] == "2d"):
            show_plot_2d(dataset.read_csv(
                sys.argv[1]), *[float(x) for x in sys.argv[3:6]])
        else:
            show_plot_3d(dataset.read_csv(
                sys.argv[1]), *[float(x) for x in sys.argv[3:5]])
