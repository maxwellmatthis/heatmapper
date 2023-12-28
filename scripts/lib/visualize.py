#!/usr/bin/python3
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib
from lib.dataset import ValueType, MergedMeasurementTable
from typing import *


def makeScalarMap(value_type: ValueType):
    best_possible_value = value_type.best_possible_value
    worst_possible_value = value_type.worst_possible_value

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


def figure_name(dimension_type: str, name: Optional[str], table: MergedMeasurementTable):
    return f"{dimension_type} Plot of " \
        + (f"{table.value_type.name} in {table.value_type.unit}"
           + f" filtered by \"{table.filter_expression}\""
           if name is None else f"\"name\"")


def show_plot_3d(
    table: MergedMeasurementTable,
    name: str = None,
):
    """
    Displays a dataset in 3D space using matplotlib.

    The points will be colored based on the best and worst possible values.
    Green is the best, yellow is medium, and red ist the worst.
    """
    _ids, x_vals, y_vals, z_vals, values = zip(*table.rows)

    # graph
    fig = plt.figure()
    fig.suptitle(figure_name("3D", name, table))
    ax = fig.add_subplot(projection='3d')
    ax.scatter(x_vals, y_vals, z_vals, c=makeScalarMap(
        table.value_type).to_rgba(values))
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
    Green is the best, yellow is medium, and red ist the worst.
    """
    _ids, x_vals, y_vals, z_vals, values = zip(*table.rows)
    # default: flatten Axis.Z
    xy2d = [x_vals, y_vals]
    if ignore_axis == Axis.X:
        xy2d = [y_vals, z_vals]
    elif ignore_axis == Axis.Y:
        xy2d = [x_vals, z_vals]

    # graph
    fig, ax = plt.subplots()
    fig.suptitle(figure_name(f"2D ({ignore_axis} flattened)", name, table))
    ax.scatter(*xy2d, c=makeScalarMap(table.value_type).to_rgba(values))
    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    plt.show()
