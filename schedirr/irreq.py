# -*- coding: latin-1 -*-
# Copyright (c) 2023 WUR, Wageningen
""" irreq - a Python module for making calculations with regard to irrigation scheduling """
from typing import NewType, TypeVar, List, Tuple
from collections.abc import Sequence
from pathlib import Path
from array import array
from math import floor
from cropstage import CropStage
from configparser import ConfigParser
from sys import argv
from customtypes import PathLike, ArrayLike 
from fileinput import TextInputReader

__author__ = "Steven B. Hoek"

# Declare constants
eps: float = 0.0000001
smallreal: float = 0.02

def water_balance(M:int, ET0:float, RE:float, PR:float, ep:float, Kc0, SR0, DR, AF, ATF) -> float:
    # Calculate the gross irrigation requirement for this month
    
    # Check the input
    assert (sum(ATF) - 1.0) < eps, "The sum of the area time fractions is greater than 1.0!"

    # Water requirements
    CRQ: array = array('f', M * [0.0]) # Consumptive requirements
    ORQ: array = array('f', M * [0.0]) # Ordinary requirements
    SRQ: array = array('f', M * [0.0]) # Special requirements
    IRQ: array = array('f', M * [0.0]) # Irrigation requirement

    # Natural supply and irrigation
    WS: array = array('f', M * [0.0]) # Natural water supply
    RD: array = array('f', M * [0.0]) # Rainfall deficit
    RS: array = array('f', M * [0.0]) # Rainfall surplus
    
    for k in range(M):
        # Calculate the water requirements
        CRQ[k] = Kc0[k] * ET0
        if Kc0[k] > 0.0: ORQ[k] = CRQ[k] + PR
        else: ORQ[k] = CRQ[k] # assume that there's no percolation in this case
         
        # Calculate the special requirements
        SRQ[k] = AF[k] * SR0[k]
        
        # Calculate the replenishment and irrigation items
        WS[k] = RE + DR[k]
        RD[k] = ATF[k] * max(0, ORQ[k] - WS[k]) 
        IRQ[k] = RD[k] + SRQ[k]
        
        # There may be a surplus, but for the meantime, we assume there's no local storage
        #RS[k] = ATF[k] * max(WS[k] - ORQ[k])
    
    result = sum(IRQ) / ep
    return result

# Input data wrt. environment and crop calendar may be lists of normal arrays or lists of numpy arrays
def irr_proc(u1:int, un:int, sp:float, ep:float, env_data:Sequence[ArrayLike], stage_data:Sequence[ArrayLike]):
    # Declare
    arr: ArrayLike
    
    # Dimension the arrays - internally we'll work with normal arrays
    umax = len(env_data)
    ET0: array = array('f', umax * [0.0]) # evapotranspiration
    RE: array =  array('f', umax * [0.0]) # effective rainfall
    PR: array =  array('f', umax * [0.0]) # percolation requirement
    
    # Read the environmental data - assume this order: ET0, rainfall and percolation
    for i in range(umax):
        arr = env_data[i]
        ET0[i], RE[i], PR[i] = arr[0], arr[1], arr[2]
            
    # Dimension the arrays - internally we'll work with normal arrays
    vmax = len(stage_data)
    D:  array =  array('f', vmax * [0.0]) # duration
    Kc: array = array('f', vmax * [0.0]) # crop coefficient
    SR: array = array('f', vmax * [0.0]) # special requirement
    DS: array = array('f', vmax * [0.0]) # depletion of stored water
    
    # Read the data wrt. the crop calendar - assume this order: duration, crop coefficient,
    # special requirement and depletion
    for i in range(vmax):
        arr = stage_data[i]
        D[i], Kc[i], SR[i], DS[i] = arr[0], arr[1], arr[2], arr[3]

    # Check spreading period
    if sp > umax:
        raise ValueError("The spreading period is greater than the total number of periods!")
    
    # Check that the periods and crop stages are somehow in accordance with each other
    # Also calculate N - the number of crop stages per period
    qr: Tuple[int, int] = divmod(vmax, umax)
    if qr[1] == 0: N = qr[0]
    else: raise NotImplementedError("Not able to handle the input")
        
    # Calculate L and M
    # L: in the current period L earlier periods should (also) be considered because stages continue in this period
    # M: max. number of stages that can coincide with a period
    L: int = floor(sp - eps) + 1
    M: int = (L + 1) * N
    
    # Do a check on the input data for each month
    u: int # period number, not 0-based but 1-based!
    for u in range(1, umax+1):
        # Check that for each period holds that the sum of the duration is approx. equal to 1.0
        # i.e. in all stages v =  that start in period u
        if sum(D[u*N: (u+1)*N]) - 1.0 > smallreal:
            raise ValueError("The sum of crop stage durations over month %s differs to much from 1.0" % (u+1))
        
        # Check that for each period ET0, effective rainfall and the percolation requirement is greater than zero
        assert ET0[u-1] >= 0.0, "Value for ET0 is lower than 0.0 for month %s!" % u
        assert RE[u-1] >= 0.0, "Value for RE is lower than 0.0 for month %s!" % u
        assert PR[u-1] >= 0.0, "Value for PR is lower than 0.0 for month %s!" % u
        
    # Also check the crop cultural data
    v: int # stage index, 0-based
    for v in range(vmax):
        assert D[v] >= 0.0, "Duration of stage %s is lower than 0.0!" % (v+1)
        assert Kc[v] >= 0.0, "Value of crop coefficient for stage %s is lower than 0.0!" % (v+1)
        assert SR[v] >= 0.0, "Value of special requirement for stage %s is lower than 0.0!" % (v+1)
        assert DS[v] >= 0.0, "Value of moisture depletion for stage %s is lower than 0.0!" % (v+1)  
    
    # Prepare the crop stages
    cs: CropStage
    cropstages = []
    for v in range(vmax):
        qr = divmod(v, N)
        if qr[1] == 0: time = 0.0
        else: time = sum(D[qr[0] * N:v])
        cs = CropStage(startperiod = floor(1 + v / N), time = time, duration = D[v], sp = sp)
        cropstages.append(cs) # can be retrieved again using zero-based index

    # Prepare local arrays for crop coefficient, special reqs. and depletion
    Kc0: array = array('f', M * [0.0]) # crop coefficient
    SR0: array = array('f', M * [0.0]) # special requirement (e.g. in mm)
    DR: array = array('f', M * [0.0]) # depletion rate of stored water (e.g. in mm/day)
    AF:  array = array('f', M * [0.0]) # Area fraction
    ATF: array = array('f', M * [0.0]) # Area time fraction
        
    if u1 <= un:
        result = array('f', umax * [0])
        for u in range(u1, un+1):
            # To calculate the necessary things, we will need M figures for each month
            for k in range(M):
                v = (u - L - 1) * N + k
                if v < 0: v += vmax
                Kc0[k] = Kc[v]
                SR0[k] = SR[v]
                cs = cropstages[v]
                if cs.duration > 0.0: DR[k] = DS[v] / cs.duration
                else: DR[k] = 0.0
                AF[k] = cs.area_fraction(u)
                ATF[k] = cs.area_time_fraction(u)
            result[u-1] = round(water_balance(M, ET0[u-1], RE[u-1], PR[u-1], ep, Kc0, SR0, DR, AF, ATF), 3)
        print(result)
    else:
        raise NotImplementedError("Not able to handle function call with u1 > un!")

if __name__ == "__main__":
    # Get the name of the configuration file
    config = ConfigParser()
    if len(argv) == 1:
        # Assume that input is taken from file params.ini
        ini_fn = "params.ini"
    else:
        ini_fn = str(argv[1])
    if not Path(ini_fn).exists(): ValueError("File %s not found!")
    
    # Declare
    fn_enviro: PathLike
    fn_cropcult: PathLike
    
    # Prepare to read the input files
    config.read(ini_fn)
    if 'FilenameEnvironmentalData' in config['DEFAULT']:
        fn_enviro = config['DEFAULT']['FilenameEnvironmentalData']
        fn_enviro = Path(fn_enviro)
        if not fn_enviro.exists(): raise ValueError("Filename with environmental data not found!")
    if 'FilenameCropCalendarData' in config["DEFAULT"]:
        fn_cropcult = config['DEFAULT']['FilenameCropCalendarData']
        fn_cropcult = Path(fn_cropcult)
        if not fn_cropcult.exists(): raise ValueError("Filename with crop calendar not found!")
    
    try:
        # Periods are 1-based, so 1 is for January etc.
        if 'FirstMonth' in config['DEFAULT']:
            u1: int = int(config['DEFAULT']['FirstMonth'])
        else:
            ValueError('Key FirstMonth missing in configuration')
        if 'LastMonth' in config['DEFAULT']:
            un: int = int(config['DEFAULT']['LastMonth'])
        else:
            ValueError('Key LastMonth missing in configuration')
        if 'SpreadingPeriod' in config['DEFAULT']:
            sp: float = float(config['DEFAULT']['SpreadingPeriod'])
        else:
            ValueError('Key SpreadingPeriod missing in configuration')
        if 'Efficiency' in config['DEFAULT']:
            ep: float = float(config['DEFAULT']['Efficiency'])
        else:
            ValueError('Key Efficiency missing in configuration')          
    
    except Exception as e:
        print(e) 
        raise Exception(e)

    # Now read the input files    
    tir = TextInputReader()
    env_data = tir.read_env_data(fn_enviro)
    stage_date = tir.read_crop_stages(fn_cropcult)
    irr_proc(u1, un, sp, ep, env_data, stage_date)
