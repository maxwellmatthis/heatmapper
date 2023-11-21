#!/usr/bin/python3
import dataset

FILENAME = "test-large.csv"

dataset.write_csv(FILENAME, dataset.generate_random_dataset(100, 100, 100, 20, 2))
dataset.append_csv(FILENAME, -1, -2, -3, 1234)
print(dataset.read_csv(FILENAME))
