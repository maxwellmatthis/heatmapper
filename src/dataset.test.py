#!/usr/bin/python3

import dataset

FILENAME = "test-large.csv"

dataset.write_csv(FILENAME, dataset.generate_random_dataset(100, 100, 100, 1000, 2))
print("First twenty vectors:", dataset.read_csv(FILENAME)[:20])
