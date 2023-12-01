#!/usr/bin/python3
from typing import *
from dataset import Dataset, Instrument, ValueType, Coordinates, Value, MergeFunction

# Prepare and Save
test_type = ValueType("test_type", "imaginary test unit", 100, 0)


def test_vals(*vals: List[float]): return dict(
    (f"test_value_{i}", Value(test_type, vals[i])) for i in range(len(vals)))


instrument_name = "Test Instrument"
INS = Instrument(instrument_name, {"meta": "data"}, [test_type], test_vals)
DS = Dataset("The Great Testing Dataset",
             "This is the description of the test dataset.").add_instrument(INS)

INS.take_measurement(Coordinates(0, 1, 2), None, 30)
INS.take_measurement(Coordinates(
    1, 2, 3), "This is the measurement with the three values.", 80, 60, 40)
INS.take_measurement(Coordinates(3, 2, 1), None, 50)

DS.save()

# Load
DS2 = Dataset.load("the-great-testing-dataset.json")
INS2 = DS2.get_instrument(instrument_name)

print(INS2.measurements_as_table("test", MergeFunction.accumulate).csv())
print(INS2.measurements_as_table("1|2").csv())

INS2.take_measurement(Coordinates(0, 0, 0))
