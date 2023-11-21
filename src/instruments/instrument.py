#!/usr/bin/python3
from abc import ABC, abstractmethod


class Instrument(ABC):
    @abstractmethod
    def measure() -> float | None:
        pass
