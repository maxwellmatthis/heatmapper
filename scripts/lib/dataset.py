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

from dataclasses import dataclass
import sys
import signal
import random
import math
from typing import *
import uuid
import json
import datetime
import re
import inspect


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
                and not key.startswith("_abc_impl")
            )
            return self.default(d)
        return obj


@dataclass
class ValueType:
    name: str
    unit: str
    best_possible_value: float
    worst_possible_value: float

    def from_dict(d: dict) -> Self:
        return ValueType(d["name"], d["unit"], d["best_possible_value"], d["worst_possible_value"])


ValueTypes = Dict[str, ValueType]


@dataclass
class Coordinates:
    x: float
    y: float
    z: float

    def from_dict(d: dict) -> Self:
        return Coordinates(d["x"], d["y"], d["z"])


@dataclass
class Value:
    type: str
    value: float

    def __init__(self, value_type: ValueType | str, value: float):
        self.type = value_type.name if isinstance(
            value_type, ValueType) else value_type
        self.value = value

    def from_dict(d: dict) -> Self:
        return Value(d["type"], d["value"])


Values = Dict[str, Value]


@dataclass
class Measurement:
    id: str
    coordinates: Coordinates
    values: Values
    note: Optional[str]

    def new(coordinates: Coordinates, values: Values, note: Optional[str]) -> Self:
        return Measurement(str(uuid.uuid4()), coordinates, values, note)

    def from_dict(d: dict) -> Self:
        id = d["id"]
        coordinates = Coordinates.from_dict(d["coordinates"])
        values = dict((k, Value.from_dict(v)) for k, v in d["values"].items())
        note = d["note"]
        return Measurement(id, coordinates, values, note)


Measurements = List[Measurement]


class MergeFunction:
    def greater(x: float, greatest: float) -> bool: return x > greatest
    def lesser(x: float, least: float) -> bool: return x < least
    def accumulate(
        x: float, accumulator: float) -> float: return float(x + accumulator)


MergedMeasurementTableRow = Tuple[str, float, float, float, float]


@dataclass
class MergedMeasurementTable:
    filter_expression: str
    value_type: ValueType
    rows: List[MergedMeasurementTableRow]

    def csv(self) -> str:
        return "\n".join([
            ",".join(["id", "x", "y", "z", self.value_type.name]),
            *(",".join([str(val) for val in [*row]]) for row in self.rows)
        ])


Meta = Dict[str, Any]


@dataclass
class Instrument():
    name: str
    meta: Meta
    value_types: ValueTypes
    measurements: Measurements
    do_measure_function: Any

    def __init__(self, name: str, meta: Meta, value_types: List[ValueType], do_measure_function: Any):
        self.name = name
        self.meta = meta
        self.value_types = dict((value_type.name, value_type)
                                for value_type in value_types)
        self.measurements = []
        self.do_measure_function = do_measure_function

    def from_dict(d: dict) -> Self:
        i = Instrument(
            d["name"],
            d["meta"],
            list(ValueType.from_dict(value_type)
                 for value_type in d["value_types"].values()),
            lambda: print(
                "You'll need to overwrite the `do_measure_function` to measure new values because the measurement function cannot be stored as JSON.")
        )
        i.measurements = list((Measurement.from_dict(v))
                              for v in d["measurements"])
        return i

    def get_value_type(self, name: str) -> ValueType:
        return self.value_types[name]

    def take_measurement(self, coordinates: Coordinates, note: str = None, *args) -> Optional[Measurement]:
        try:
            measurement = Measurement.new(
                coordinates, self.do_measure_function(*args), note)
            self.measurements.append(measurement)
            return measurement
        except Exception as e:
            print(e)


    def __merge_columns(self, columns: Dict[str, Value], merger) -> float:
        saved_value: float = None
        for _, value in columns:
            if saved_value is None:
                saved_value = value.value
            else:
                merge_value = merger(value.value, saved_value)
                if isinstance(merge_value, float):
                    saved_value = merge_value
                elif merge_value == True:
                    saved_value = value.value
        return saved_value

    def measurements_as_table(
        self,
        filter_expression: str = ".",
        merger=MergeFunction.greater
    ) -> MergedMeasurementTable:
        pat = re.compile(filter_expression)
        rows = []
        none_matched = True
        value_type_name = None
        for measurement in self.measurements:
            matching_columns = list(
                filter((lambda k_v: pat.search(k_v[0]) is not None), measurement.values.items()))
            if len(matching_columns) >= 1:
                # infer value data type from first matching column
                if value_type_name is None:
                    first_row = matching_columns[0]
                    value_type_name = first_row[1].type
                # todo: maybe add a warning if too many values are excluded?
                commonly_typed_columns = list(filter(
                    (lambda k_v: k_v[1].type == value_type_name), matching_columns))
                none_matched = False
                c = measurement.coordinates
                rows.append(
                    [measurement.id, c.x, c.y, c.z, self.__merge_columns(commonly_typed_columns, merger)])
        if none_matched:
            print("WARNING: No column matched your filter expression.")
        return MergedMeasurementTable(filter_expression, self.get_value_type(value_type_name), rows)


Instruments = Dict[str, Instrument]


@dataclass
class Dataset:
    name: str
    created: str
    description: str
    instruments: Instruments

    def __init__(self, name: str, description: str = "none provided"):
        self.name = name
        self.created = datetime.datetime.now().isoformat()
        self.description = description
        self.instruments = {}

    def enable_save_on_terminate(self):
        def gracefully_die(*args):
            self.save()
            exit(0)
        signal.signal(signal.SIGINT, gracefully_die)
        signal.signal(signal.SIGTERM, gracefully_die)

    def load(path: str) -> Self:
        """
        Reads a `dataset` from a file at a given `path`.
        """
        with open(path, "r") as file:
            raw_ds = json.loads(file.read())
            ds = Dataset(raw_ds["name"])
            if "created" in raw_ds:
                ds.created = raw_ds["created"]
            if "description" in raw_ds:
                ds.description = raw_ds["description"]
            if "instruments" in raw_ds:
                ds.instruments = dict((k, Instrument.from_dict(v))
                                      for k, v in raw_ds["instruments"].items())
            return ds

    def make_safe_file_name(name: str):
        return re.sub("\/| ", "-", str(name)).lower()[:30]

    def save(self) -> str:
        """
        Saves the dataset as JSON.
        """
        filename = Dataset.make_safe_file_name(self.name) + ".json"
        with open(filename, "w") as file:
            file.write(json.dumps(self, cls=ObjectEncoder,
                       indent=2, sort_keys=True))
        return filename

    def get_instrument(self, name: str):
        return self.instruments[name]

    def add_instrument(self, instrument: Instrument) -> Self:
        if instrument.name in self.instruments:
            raise Exception(
                f"Instrument {instrument.name} already exists. Try editing it instead.")
        self.instruments[instrument.name] = instrument
        return self


def __distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
    """
    Returns the distance between two vectors using the pythagorean theorem.
    """
    return math.sqrt(
        (a[0] - b[0])**2
        + (a[1] - b[1])**2
        + (a[2] - b[2])**2
    )


AREA_WIDTH = 100.0
AREA_HEIGHT = 100.0
AREA_DEPTH = 100.0
DEFAULT_MEASUREMENT_COUNT = 500
DEFAULT_EMITTER_COUNT = 2


def generate_random_dataset(
    measurement_count: int = DEFAULT_MEASUREMENT_COUNT,
    emitter_count: int = DEFAULT_EMITTER_COUNT,
    value_function_and_output_type=(lambda d: d, ValueType(
        "value_function_output", "m", 0, (AREA_DEPTH + AREA_HEIGHT + AREA_WIDTH) / 2))
) -> Dataset:
    """
    Generates a random dataset with `measurement_count` data points and `emitter_count` emitter
    in a space of size `area_depth * area_width * area_height` and computes the measurement
    values for each data point based on the distance to the closest emitter and the `value_function`.
    """
    # generate random coordinates
    x_coordinates = list(random.random() *
                         AREA_DEPTH for _ in range(measurement_count))
    y_coordinates = list(random.random() *
                         AREA_WIDTH for _ in range(measurement_count))
    z_coordinates = list(random.random() *
                         AREA_HEIGHT for _ in range(measurement_count))

    random.shuffle(x_coordinates)
    random.shuffle(y_coordinates)
    random.shuffle(z_coordinates)

    coordinates = list(zip(x_coordinates, y_coordinates, z_coordinates))

    # compute values
    emitters = [(random.random() * AREA_WIDTH, random.random() * AREA_HEIGHT,
                 random.random() * AREA_DEPTH) for _ in range(emitter_count)]

    # create dataset
    value_function, value_function_output_type = value_function_and_output_type

    def do_measure(x, y, z) -> Values:
        values = {}
        for i in range(len(emitters)):
            values[f"e{i}"] = Value(
                value_function_output_type, value_function(__distance((x, y, z), emitters[i])))
        return values

    INS = Instrument("random_data", {
        "area_width": AREA_WIDTH,
        "area_height": AREA_HEIGHT,
        "area_depth": AREA_DEPTH,
        "measurement_count": measurement_count,
        "emitter_count": emitter_count
    }, [value_function_output_type], do_measure)
    DS = Dataset("Random Test Dataset").add_instrument(INS)

    for x, y, z in coordinates:
        INS.take_measurement(Coordinates(x, y, z), None, x, y, z)
    return DS


if __name__ == "__main__":
    generate_random_dataset().save()
