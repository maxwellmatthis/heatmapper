#!/usr/bin/python3
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from lib.dataset import MergedMeasurementTable, ValueType
from typing import *

def __get_cmap(value_type: ValueType) -> str:
    # higher is better mode
    if value_type.best_possible_value >= value_type.worst_possible_value:
        return "Spectral"
    # lower is better mode
    else:
        return "Spectral_r"


def __figure_name(dimension_type: str, name: Optional[str], table: MergedMeasurementTable):
    filter_expressions = ", ".join([("\"" + fe + "\"") for fe in table.filter_expressions])
    return f"{dimension_type} Plot of " \
        + (f"{table.value_type.name} in {table.value_type.unit}"
           + f" filtered by {filter_expressions}"
           if name is None else f"\"name\"")


def show_plot_3d(
    table: MergedMeasurementTable,
    name: str = None,
):
    """
    Displays a dataset in 3D space using matplotlib.

    The points will be colored based on the best and worst possible values.
    """
    _ids, x_vals, y_vals, z_vals, values = zip(*table.rows)

    # graph
    fig = plt.figure()
    fig.suptitle(__figure_name("3D", name, table))
    ax = fig.add_subplot(projection='3d')
    ax.scatter(x_vals, y_vals, z_vals, c=values, cmap=__get_cmap(table.value_type))
    ax.set_aspect("equal")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    plt.show()


@dataclass
class Axis:
    X = "x"
    Y = "y"
    Z = "z"


DEFAULT_FLATTENING_AXIS = Axis.Z


def show_plot_2d(
    table: MergedMeasurementTable,
    ignore_axis: str = DEFAULT_FLATTENING_AXIS,
    name: str = None
):
    """
    Displays a dataset in 2D space using matplotlib.
    flattening the x-axis gives a straight-on view;
    flattening the y-axis gives a left to right view;
    Flattening the z-axis gives a top down view.

    The points will be colored based on the best and worst possible values.
    """
    _ids, x_vals, y_vals, z_vals, values = zip(*table.rows)
    # default: flatten Axis.Z
    xy2d = [x_vals, y_vals]
    if ignore_axis == Axis.X:
        xy2d = [y_vals, z_vals]
    elif ignore_axis == Axis.Y:
        xy2d = [x_vals, z_vals]

    # graph
    scatter = plt.scatter(*xy2d, c=values, cmap=__get_cmap(table.value_type))
    plt.grid(True)
    plt.axis('equal')

    plt.colorbar(
        scatter,
        orientation='vertical',
        label=f"{table.value_type.name} in {table.value_type.unit}",
        ticks=np.linspace(table.value_type.best_possible_value, table.value_type.worst_possible_value, 20)
    )
    plt.suptitle(__figure_name(f"2D ({ignore_axis} flattened)", name, table))
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.show()
