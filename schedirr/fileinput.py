# -*- coding: latin-1 -*-
# Copyright (c) 2023 WUR, Wageningen
""" fileinput - a Python module for reading input data from text, CSV and TSV files """
from typing import NewType, TypeVar, List, Tuple
from collections.abc import Iterable, Sequence
from pathlib import Path
from array import array
from customtypes import PathLike, ArrayLike
import copy
import csv

__author__ = "Steven B. Hoek"

class InputReader(object):
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])]
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])]
    
class TextInputReader(InputReader):   
    # Read the data wrt. climate and soil; assume a text file
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        # Local variables
        i: int
        buf: List[str]
        lines: List[str]
        
        # Read the lines
        with open(fn, 'r', encoding="utf-16") as enviro:
            # Read all lines but remove empty ones
            buf = enviro.readlines()
            lines = [r for r in buf if not r.isspace()]
            umax: int = len(lines[1:])
        
        # Prepare the output structure    
        result: Sequence[ArrayLike] = []
        for u in range(umax): 
            result.append(copy.deepcopy(array('f', 3 * [0.0]))) # type: ignore
        
        # Split the lines and assign the values
        for i, line in zip(range(umax), lines[1:]):
            dummy, v1, v2, v3 = line.split() # dummy and 3 values
            result[i][0], result[i][1], result[i][2] = float(v1), float(v2), float(v3)
        return result
    
    # Read data wrt. the crop stages
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        # Local variables
        i: int
        buf: List[str]
        lines: List[str]
        
        # Read the lines
        with open(fn, 'r', encoding="utf-16") as cropcult:
            # Read all lines but remove empty ones
            buf = cropcult.readlines()
            lines = [r for r in buf if not r.isspace()]
            vmax: int = len(lines[1:])
        
        # Prepare the output structure
        result: Sequence[ArrayLike] = []
        for v in range(vmax): 
            result.append(copy.deepcopy(array('f', 4 * [0.0]))) # type: ignore
        
        # Split the lines and assign the values
        for i, line in zip(range(vmax), lines[1:]):
            dummy, v1, v2, v3, v4 = line.split() # dummy and 3 values
            result[i][0], result[i][1], result[i][2], result[i][3] = float(v1), float(v2), float(v3), float(v4)
        return result 
    
class CsvInputReader(InputReader):
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        # TODO: use csv.reader
        return [array('f', [-1.0])]
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])]
    
class TsvInputReader(InputReader):
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        # TODO: use csv reader as follows 
        # tsv_file = csv.reader(file, delimiter="\t")
        return [array('f', [-1.0])]
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])]
