# -*- coding: latin-1 -*-
# Copyright (c) 2023 WUR, Wageningen
""" cropstage - a Python module with a class that represents a crop stage """
from typing import NewType, TypeVar, List, Tuple
from array import array
from math import floor, ceil
eps = 0.0000001

__author__ = "Steven B. Hoek"      
        
class CropStage(object):
    '''
    Class for representing a paralellogram that symbolises a stage of an irrigated 
    crop in a tertiary irrigation unit. It is assumed that the area with the crop 
    is gradually expanded when it's planted. The time it takes for the whole 
    tertiary unit to be planted with the crop is called the spreading period (sp). 
    It may take more than period (e.g. month), so the parameter sp may be greater 
    than 1. There may be more than one crop stage per period - each starting a 
    certain time after the beginning of the period. Every period has the same
    number of crop stages. The duration of a crop stage may be equal to 0, so
    that it has no real effect on the calculations. The diagram below shows the 
    situation somehow - with the area represented vertically and the time re-
    presented horizontally. The periods - e.g. months are counted as 1 ..12 or so.
    Aim of it all is to calculate how the crop stages intersect with the periods
    (e.g. months).
    A --------- B ----------E ----------G 
    |   .       |   .       |   .       |
    |       .   |       .   |       .   |
    D-----------C-----------F-----------H       
    '''
    
    __sp: float = 1
    __start: int = 0
    __time: float = 0.0
    __duration: float = 1
    
    def __init__(self, startperiod: int, time: float, duration: float, sp:float):
        # Check input
        if time > 1.0: raise ValueError("Time cannot be greater than 1.0!")
        if duration > 1.0: raise ValueError("Duration cannot be greater than 1.0!")
        if sp == 0.0: raise ValueError("Spreading period cannot be equal to 1.0!")
        if time + duration > 1.0: 
            raise ValueError("The sum of time and duration cannot be greater than 1.0!")
        
        self.__start: int = startperiod
        self.__time = time
        self.__duration: float = duration
        self.__sp: float = sp

    # Which part of the stage initialisation occurs in the current period?
    def area_fraction(self, period:int) -> float:
        # Initialise
        result: float = 0.0
        
        # Distinguish between the cases sp <= 1 and sp > 1
        if self.__sp <= 1:
            if period == self.__start:
                if (self.__sp + self.__time) <= 1.0:
                    result = 1.0
                else:
                    result = (1 - self.__time) / self.__sp
            elif period == self.start + 1:
                if (self.__sp + self.__time) > 1.0:
                    result = (self.__sp + self.__time - 1.0) / self.__sp
        else:
            L: int # length of time that we need to consider
            if self.__time == 0.0:
                # For how many months do we need to look back in time?
                L = floor(self.__sp - eps) + 1
                if period == self.__start: 
                    result = 1.0 / self.__sp
                elif period == floor(self.start + self.__sp - eps):
                    # Last period during which the stage occurs
                    result = (self.__sp - L + 1) / self.__sp
                elif period < L + 1:
                    result = 1.0 / self.__sp    
            else: 
                # For how many months do we need to look back in time?
                L = floor(self.__sp + self.__time - eps) + 1
                if period == self.__start:
                    result = (1.0 - self.__time) / self.sp
                elif period == floor(self.start + self.__time + self.__sp - eps):
                    # Last period during which the stage occurs
                    result = (self.__sp + self.__time - L + 1) / self.__sp
                elif period < L + 1:
                    result = 1.0 / self.__sp            
        return result
        
    def area_time_fraction(self, period:int) -> float:
        # We want to know what part of the area * time in this period is covered by this crop stage
        result: float = 0.0
        base: float = 0.0
        height: float = 0.0
        b: float = 0.0
        h: float = 0.0
        
        # Distinguish between the cases sp <= 1 and sp > 1
        if self.__sp <= 1:
            if period == self.__start:
                if (self.__sp + self.__time + self.__duration) <= 1.0:
                    # This stage ends in this period 
                    result = self.__duration * 1.0 # paralellogram
                elif (self.__sp + self.__time) <= 1.0:
                    # The last farmer starts this stage but ends it in the next one
                    result = self.__duration * 1.0 # paralellogram
                    b = self.__time + self.__sp + self.__duration - 1
                    h = b / self.__sp
                    result = result - 0.5 * b * h 
                else:
                    # The last farmer starts and ends this stage in the next period 
                    af = self.area_fraction(period)
                    base = af * self.__sp
                    height = af / self.__sp
                    b = 1 - self.__time - self.__duration
                    h = b / self.__sp
                    result = 0.5 * base * height - 0.5 * b * h
            elif period == self.start + 1:
                # By all means, this stage ends in this period 
                af = self.area_fraction(period)
                b = af * self.__sp
                h = af
                base = b + self.__duration 
                height = base / self.__sp
                result = 0.5 * base * height - 0.5 * b * h
        else:
            # For how many months back do we need to look back? 
            L: int = floor(self.__sp - eps) + 1
            
            # We're going to determine the areas by considering various triangles
            if period == self.__start:
                af = self.area_fraction(period)
                base = af * self.__sp
                height = af
                if self.__time + self.__duration <= 1.0:
                    # We need to subtract the area of the upper left corner 
                    b = (1.0 - self.__time - self.__duration)
                    h = b / self.__sp
                result = 0.5 * base * height - 0.5 * b * h
            elif period == floor(self.__start + self.__time + self.__duration + self.__sp - eps):
                # Last period during which the stage occurs
                base = self.__start + self.__time + self.__duration + self.__sp - L - 1
                height = base / self.__sp
                af = self.area_fraction(period) 
                b = af * self.__sp
                h = af
                result = 0.5 * base * height - 0.5 * b * h
            elif period == floor(self.__start + self.__time + self.__duration + self.__sp - eps) - 1:
                # Last but one period: the result should be the area of a trapezium minus another area  
                at = self.area_fraction(period) 
                if abs(1 - at * self.__sp) > eps:
                    # The last farmer starts this stage in this period and ends it in the next period
                    b = at * self.__sp
                    h = at
                    base = 1
                    h1 = h + self.__duration / self.__sp
                    h2 = self.area_fraction(period) 
                    result = (0.5 * base * (h1 + h2) / 2) - 0.5 * b * h
                else:
                    # Other periods - assume that we're dealing with a parallelogram
                    base = at * self.__sp
                    height = self.__duration / self.__sp
                    result = base * height
            else:
                # The result is the area of a paralellogram
                at = self.area_fraction(period) 
                base = at * self.__sp
                height = self.__duration / self.__sp
                result = base * height
            
        return result
        
    @property
    def sp(self) -> float:
        return self.__sp
    
    @property
    def start(self) -> float:
        return self.__start
    
    @property
    def duration(self) -> float:
        return self.__duration
    
    @property
    def time(self) -> float:
        return self.__time    
        
if __name__ == "__main__":
    print("This is module cropstage from package schedirr.")
    print("Run unit tests test_area_fractions and test_area_time_fractions to test the code of this module.")