#!/usr/bin/python3
"""
# Dataset Format

Datasets are represented as an array of four-dimensional vectors.
Each vector is made up of the following:

- x [m] (near to far from observer),
- y [m] (left to right from observer),
- z [m] (floor to ceiling from observer),
- value (measurement, e.g. intensity of light; used to compare points or color them in visualizations)
- (optional) id [uuid] of measurement
"""

import sys
import os
import csv
import random
import math
from typing import *
import uuid

VECTOR_TYPE = Tuple[float, float, float]
MEASUREMENT_TYPE = Tuple[float, float, float, float, str]
DATASET_TYPE = List[MEASUREMENT_TYPE]
FIELDNAMES = ["x", "y", "z", "value", "id"]


def read_csv(path: str) -> DATASET_TYPE:
    """
    Reads a `dataset` from a file at a given `path`.
    """
    dataset = []
    with open(path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dataset.append((
                float(row["x"]),
                float(row["y"]),
                float(row["z"]),
                float(row["value"]),
                str(row["id"])
            ))
    return dataset


def write_csv(path: str, dataset: DATASET_TYPE):
    """
    Writes a `dataset` to a file at a given `path`.
    """
    with open(path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for x, y, z, value, id in dataset:
            writer.writerow({"x": x, "y": y, "z": z, "value": value, "id": id})


def append_csv(path: str, x: float, y: float, z: float, value: float) -> str:
    id = uuid.uuid4()
    if not os.path.exists(path):
        with open(path, "a") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
    with open(path, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writerow({"x": x, "y": y, "z": z, "value": value, "id": id})
    return id


def __distance(a: VECTOR_TYPE, b: VECTOR_TYPE) -> float:
    """
    Returns the distance between two vectors using the pythagorean theorem.
    """
    return math.sqrt(
        (a[0] - b[0])**2
        + (a[1] - b[1])**2
        + (a[2] - b[2])**2
    )


DEFAULT_AREA_WIDTH = 100.0
DEFAULT_AREA_HEIGHT = 100.0
DEFAULT_AREA_DEPTH = 100.0
DEFAULT_MEASUREMENT_COUNT = 1000
DEFAULT_EMITTER_COUNT = 2


def generate_random_dataset(
    area_width: float = DEFAULT_AREA_WIDTH,
    area_height: float = DEFAULT_AREA_HEIGHT,
    area_depth: float = DEFAULT_AREA_DEPTH,
    measurement_count: int = DEFAULT_MEASUREMENT_COUNT,
    emitter_count: int = DEFAULT_EMITTER_COUNT,
    value_function=lambda d: d
) -> DATASET_TYPE:
    """
    Generates a random dataset with `measurement_count` data points and `emitter_count` emitter
    in a space of size (`area_width` by `area_height` by `area_depth`) and computes the measurement
    values for each data point based on the distance to the closest emitter and the `value_function`.
    """
    x_vals = list(random.random() *
                  area_width for _ in range(measurement_count))
    y_vals = list(random.random() *
                  area_height for _ in range(measurement_count))
    z_vals = list(random.random() *
                  area_depth for _ in range(measurement_count))
    ids = list(uuid.uuid4() for _ in range(measurement_count))

    random.shuffle(x_vals)
    random.shuffle(y_vals)
    random.shuffle(z_vals)

    vectors = zip(x_vals, y_vals, z_vals)
    emitters = [(random.random() * area_width, random.random() * area_height,
                 random.random() * area_depth) for _ in range(emitter_count)]
    values = list(value_function(min(__distance(v, emitter)
                  for emitter in emitters)) for v in vectors)

    return list(zip(x_vals, y_vals, z_vals, values, ids))


DEFAULT_WRITE_LOCATION = "test-dataset.csv"


def print_usage():
    print(
        f"Usage: {sys.argv[0]} "
        + f"[path/of/new-random-dataset.csv, default={DEFAULT_WRITE_LOCATION}] "
        + f"[area-width, default={DEFAULT_AREA_WIDTH}] "
        + f"[area-height, default={DEFAULT_AREA_HEIGHT}] "
        + f"[area-width, default={DEFAULT_AREA_DEPTH}] "
        + f"[measurement-count, default={DEFAULT_MEASUREMENT_COUNT}] "
        + f"[emitter-count, default={DEFAULT_EMITTER_COUNT}]"
    )


if __name__ == "__main__":
    if len(sys.argv) >= 2 and (sys.argv[1] == "help" or sys.argv[1] == "-h"):
        print_usage()
    else:
        write_csv(sys.argv[1] if len(
            sys.argv) >= 2 else DEFAULT_WRITE_LOCATION,
            generate_random_dataset(*sys.argv[2:7])
        )
