# -*- coding: latin-1 -*-
# Copyright (c) 2023 WUR, Wageningen
""" fileinput - a Python module for reading input data from text, CSV and TSV files """
from typing import NewType, TypeVar, List, Any
from collections.abc import Sequence
from pathlib import Path
from array import array 
import copy
import csv

__author__ = "Steven B. Hoek"

# Declaration of some types - needs to be repeated in every module
PathLike = TypeVar("PathLike", str, Path)
try:
    import numpy as np
    ArrayLike = TypeVar("ArrayLike", array, np.ndarray) 
except ImportError:
    ArrayLike = NewType("ArrayLike", array[Any]) # type: ignore

class InputReader(object):
    __header: str = ""
    
    def __init__(self):
        self.__header = ""
    
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])] # type: ignore
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])] # type: ignore
    
    @property
    def header(self) -> str:
        return self.__header
    
    @header.setter
    def header(self, value:str):
        self.__header = value
    
    
class TextInputReader(InputReader):    
    def __init__(self):
        InputReader.__init__(self)
       
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
        
        # Assign header
        self.header = str(lines[0].split())[1:-1].replace("'", "")
        
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
        
        # Assign header
        self.header = str(lines[0].split())[1:-1].replace("'", "")
        
        # Split the lines and assign the values
        for i, line in zip(range(vmax), lines[1:]):
            dummy, v1, v2, v3, v4 = line.split() # dummy and 3 values
            result[i][0], result[i][1], result[i][2], result[i][3] = float(v1), float(v2), float(v3), float(v4)
        return result 
    
class CsvInputReader(InputReader):
    def __init__(self):
        InputReader.__init__(self)
    
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        result: List[ArrayLike] = []
        try:
            import pandas as pd
            df = pd.read_csv(fn)
            self.header = str(df.columns.tolist())[1:-1].replace("'", "")
            colname0 = df.columns[0]
            df.drop([colname0], axis=1, inplace=True)
            for i, row in df.iterrows():
                arr: ArrayLike = row.to_numpy() # type: ignore
                result.append(arr) 
                
        except ImportError:
            print("Pandas is not installed ...")
        except Exception as e:
            print(e)
        finally:
            return result # type: ignore
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])] # type: ignore
    
class TsvInputReader(InputReader):
    def __init__(self):
        InputReader.__init__(self)
    
    def read_env_data(self, fn:PathLike) -> Sequence[ArrayLike]:
        result: List[ArrayLike] = []
        try:
            import pandas as pd
            df = pd.read_table(fn)
            self.header = str([c.strip() for c in df.columns.tolist()])[1:-1].replace("'", "")
            colname0 = df.columns[0]
            df.drop([colname0], axis=1, inplace=True)
            for i, row in df.iterrows():
                arr = row.to_numpy()
                result.append(arr) # type: ignore
                
        except ImportError:
            print("Pandas is not installed ...")
        except Exception as e:
            print(e)
        finally:
            return result
    
    def read_crop_stages(self, fn:PathLike) -> Sequence[ArrayLike]:
        return [array('f', [-1.0])] # type: ignore
    
if __name__ == "__main__":
    # Some example code
    print("This is module fileinput from package schedirr.")
    print("The following is just for testing.\n")
    
    txt_reader = TextInputReader()
    data = txt_reader.read_env_data("./tests/data/enviro.txt")
    print("The environmental data have length %s" % len(data))
    print("Header is: %s" % txt_reader.header)
    
    csv_reader = CsvInputReader()
    data = csv_reader.read_env_data("./tests/data/enviro.csv")
    print("The environmental data have length %s" % len(data))
    print("Header is: %s" % csv_reader.header)

    tsv_reader = TsvInputReader()
    data = tsv_reader.read_env_data("./tests/data/enviro.tsv")
    print("The environmental data have length %s" % len(data))
    print("Header is: %s"  % tsv_reader.header)
    