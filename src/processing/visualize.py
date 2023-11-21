#!/usr/bin/python3
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib
import dataset


DEFAULT_BEST_POSSIBLE_VALUE = 1.0
DEFAULT_WORST_POSSIBLE_VALUE = 0.0


def makeScalarMap(
    best_possible_value: float = DEFAULT_BEST_POSSIBLE_VALUE,
    worst_possible_value: float = DEFAULT_WORST_POSSIBLE_VALUE
):
    cm = None
    cNorm = None
    # higher-is-better mode
    if best_possible_value >= worst_possible_value:
        cm = plt.get_cmap('Spectral')
        cNorm = matplotlib.colors.Normalize(
            vmin=worst_possible_value, vmax=best_possible_value)
    # lower-is-better mode
    else:
        cm = plt.get_cmap('Spectral_r')
        cNorm = matplotlib.colors.Normalize(
            vmin=best_possible_value, vmax=worst_possible_value)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    return scalarMap


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

    # display
    ax.scatter(x_vals, y_vals, z_vals, c=makeScalarMap(
        best_possible_value, worst_possible_value).to_rgba(values))
    plt.show()


DEFAULT_FLATTENING_AXIS = "z"


def show_plot_2d(
    dataset: dataset.DATASET_TYPE,
    ignore_axis: str = DEFAULT_FLATTENING_AXIS,
    best_possible_value: float = DEFAULT_BEST_POSSIBLE_VALUE,
    worst_possible_value: float = DEFAULT_WORST_POSSIBLE_VALUE
):
    """
    Displays a dataset in 2D space using matplotlib.
    flattening the x-axis gives a straight-on view;
    flattening the y-axis gives a left to right view;
    Flattening the z-axis gives a top down view.

    The points will be colored based on the best and worst possible values.
    Green is the best, yellow is medium, and red ist the worst.

    Note: The `best_possible_value` does not have to be greater than the `worst_possible_value`.
    The function will automatically adapt to display the values correctly.
    """
    # graph
    x_vals, y_vals, z_vals, values, _ids = zip(*dataset)
    # default: flatten z
    xy2d = [x_vals, y_vals]
    if ignore_axis == "x":
        xy2d = [y_vals, z_vals]
    elif ignore_axis == "y":
        xy2d = [x_vals, z_vals]
    ax = plt.subplot()

    # display
    ax.scatter(*xy2d, c=makeScalarMap(best_possible_value,
               worst_possible_value).to_rgba(values))
    plt.show()


def print_usage():
    print(
        f"Usage: {sys.argv[0]} "
        + "<path/to/dataset.csv> "
        + "[\"3d\" | \"2d\", default=\"3d\"] "
        + f"[(2d-only) axis, options=\"x\", \"y\", \"z\", default=\"{DEFAULT_FLATTENING_AXIS}\"] "
        + f"[best-possible-value, default={DEFAULT_BEST_POSSIBLE_VALUE}] "
        + f"[worst-possible-value, default={DEFAULT_WORST_POSSIBLE_VALUE}]"
    )


def represents_float(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print_usage()
    else:
        if (len(sys.argv) >= 3 and sys.argv[2] == "2d"):
            hasFourthArg = len(sys.argv) >= 4
            if hasFourthArg and represents_float(sys.argv[3]):
                print(
                    "Error: Please provide an axis before providing any more optional values.")
                print_usage()
            else:
                show_plot_2d(dataset.read_csv(
                    sys.argv[1]), sys.argv[3] if hasFourthArg else DEFAULT_FLATTENING_AXIS, *[float(x) for x in sys.argv[4:6]])
        else:
            show_plot_3d(dataset.read_csv(
                sys.argv[1]), *[float(x) for x in sys.argv[3:5]])
