from typing import NewType, TypeVar, List, Tuple
from pathlib import Path
from array import array
from math import floor, max, min
from .cropstage import CropStage

# Declare types
PathLike = TypeVar("PathLike", str, Path)

# Declare constants
eps: float = 0.0000001
smallreal: float = 0.02

# This method is supposed to return 2 types of fractions: fractions to indicate which part of the total area should receive 
# the special requirement during the current month and a number of so-called area - time fractions that together with the 
# respective water depths can be used to calculate the respective water volumes that will be needed for each stage.
# There can be a special requirement during any stage. 
def time_area_char(L:int, M:int, N:int, sp:float, D0:array[float]):
    # L: lag in a particular period, the stages should be taken into account that started since the Lth preceding period
    # M: max. possible number of stages occurring in 1 period
    # N: max. number of new stages scheduled in the busiest period of the crop rotation
    areaFrac: array = array('f', M * [0.0]) 
    areatimeFrac = array = array('f', M * [0.0])

    # Perform a check on the data: no crop dev. stage should last longer than a period
    for k in range(M):
        if D0[k] < 0.0 or D0[k] > 1.0:
            errmsg = "The duration of 1 or more crop development stages as specified in the datafile containing"
            errmsg += "the crop-cultural data, is longer than a "
            raise ValueError(errmsg)
    
    # Calculate the area fractions ???
    for u in range(L):
        areaFrac[u * N] = 1.0 / sp
        for v in range(1,N):
            pass
            # areaFrac[] = sum(D0[1:N]) / sp
    for u in range(L+1):
        for k in range(N):
            pass
    
    # Calculate the time area fractions for the first N stages in the lower left corner of the diagram
    for k in range(N):
        pass
        #[k] = max(0.0, sum(D0[0:k]) + sp - L) / sp
        #ArXTav[k] = 0.5 *       
         
        pass
    
    return areaFrac, areatimeFrac

def water_balance(M:int, ET0:float, RE:float, PR:float, ep:float, Kc0:List[float], D0:List[float], SR0:List[float], DS0:List[float], Ar:List[float], Tav:List[float]) -> float:
    # Calculate the gross irrigation requirement for an assumed month

    # Water requirements
    CRQ: array = array('f', M * [0.0]) # Consumptive requirements
    ORQ: array = array('f', M * [0.0]) # Ordinary requirements
    SRQ: array = array('f', M * [0.0]) # Special requirements
    IRQ: array = array('f', M * [0.0]) # Irrigation requirement

    # Losses and supply
    DR: array = array('f', M * [0.0]) # Rate of depletion
    WS: array = array('f', M * [0.0]) # Natural water supply
    
    # Irrigation
    RD: array = array('f', M * [0.0]) # Rainfall deficit
    RS: array = array('f', M * [0.0]) # Rainfall surplus
    
    for k in range(M):
        # Calculate the water requirements
        CRQ[k] = Kc0[k] * ET0
        if Kc0[k] > 0.0: ORQ[k] = CRQ[k] + PR
        else: ORQ[k] = CRQ[k] # no percolation assumed
         
    pass
return 0

def irr_proc(u1:int, un:int, sp:float, ep:float, fn_enviro:PathLike, fn_cropcult:PathLike):
    # Local variables
    i: int
    buf: List[str]
    lines: List[str]
    
    # Read the data wrt. climate and soil
    with open(fn_enviro, 'r', encoding="utf-16") as enviro:
        # Read all lines but remove empty ones
        buf = enviro.readlines()
        lines = [r for r in buf if not r.isspace()]
        umax: int = len(lines[1:])
        
        # Dimension the arrays
        ET0: array = array('f', umax * [0.0]) # evapotranspiration
        RE: array =  array('f', umax * [0.0]) # effective rainfall
        PR: array =  array('f', umax * [0.0]) # percolation requirement 
        for i, line in zip(range(umax), lines[1:]):
            dummy, v1, v2, v3 = line.split() # dummy and 3 values
            ET0[i], RE[i], PR[i] = float(v1), float(v2), float(v3)
            
    # Read data wrt. the crop stages
    with open(fn_cropcult, 'r', encoding="utf-16") as cropcult:
        # Read all lines but remove empty ones
        buf = cropcult.readlines()
        lines = [r for r in buf if not r.isspace()]
        vmax = len(lines[1:])
        
        # Dimension the arrays
        D:  array =  array('f', vmax * [0.0]) # duration
        Kc: array = array('f', vmax * [0.0]) # crop coefficient
        SR: array = array('f', vmax * [0.0]) # special requirement
        DS: array = array('f', vmax * [0.0]) # depletion of stored water
        for i, line in zip(range(vmax), lines[1:]):
            dummy, v1, v2, v3, v4 = line.split() # dummy and 4 values
            D[i], Kc[i], SR[i], DS[i] = float(v1), float(v2), float(v3), float(v4)

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
    u: int
    for u in range(umax):
        # Check that for each period holds that the sum of the duration is approx. equal to 1.0
        # i.e. in all stages v =  that start in period u
        if sum(D[u*N: (u+1)*N]) - 1.0 > smallreal:
            raise ValueError("The sum of crop stage durations over month %s differs to much from 1.0" % (u+1))
        
        # Check that for each period ET0, effective rainfall and the percolation requirement is greater than zero
        assert ET0[u] >= 0.0, "Value for ET0 is lower than 0.0 for month %s!" % (u+1)
        assert RE[u] >= 0.0, "Value for RE is lower than 0.0 for month %s!" % (u+1)
        assert PR[u] >= 0.0, "Value for PR is lower than 0.0 for month %s!" % (u+1)
        
    # Also check the crop cultural data
    for v in range(vmax):
        assert D[v] >= 0.0, "Duration of stage %s is lower than 0.0!" % (v+ 1)
        assert Kc[v] >= 0.0, "Value of crop coefficient for stage %s is lower than 0.0!" % (v+1)
        assert SR[v] >= 0.0, "Value of special requirement for stage %s is lower than 0.0!" % (v+1)
        assert DS[v] >= 0.0, "Value of moisture depletion for stage %s is lower than 0.0!" % (v+1)  
        

    # Make local copies of the arrays for duration, crop coefficient, special reqs. and depletion
    D0:  array = array('f', M * [0.0]) # duration
    Kc0: array = array('f', M * [0.0]) # crop coefficient
    SR0: array = array('f', M * [0.0]) # special requirement
    DS0: array = array('f', M * [0.0]) # depletion of stored water
        
    if u1 <= un:
        for u in range(u1, un+1):
            # To calculate the necessary things, we will need M figures for each month
            for k in range(M):
                v = (u - L - 1) * N + k
                if v < 0: v += vmax
                D0[k] = D[v]
                Kc0[k] = Kc[v]
                SR0[k] = SR[v]
                DS0[k] = DS[v]
            arrFrac, areatimeFrac = time_area_char(L:int, M:int, N:int, sp:float, D0:array[float])
        pass
    else:
        raise NotImplementedError("Not able to handle function call with u1 > un!")

if __name__ == "__main__":
    # Periods are zero-based
    u1: int = 2 # March
    un: int = 8 # September
    sp = 2.5 # should be grater than 1
    ep = 0.8
    fn_enviro = Path("../data/enviro.txt")
    fn_cropcult = Path("../data/dry_season.txt")
    irr_proc(u1, un, sp, ep, fn_enviro, fn_cropcult)

