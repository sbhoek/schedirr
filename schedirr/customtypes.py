# -*- coding: latin-1 -*-
# Copyright (c) 2023 WUR, Wageningen
""" customtypes - a Python module with custom types"""
from typing import NewType, TypeVar
import pathlib
import array

__author__ = "Steven B. Hoek"

# Declare types
PathLike = TypeVar("PathLike", str, pathlib.Path)
try:
    import numpy as np
    ArrayLike = TypeVar("ArrayLike", array.array, np.ndarray)
except ImportError:
    ArrayLike = NewType("ArrayLike", array.array) # type: ignore