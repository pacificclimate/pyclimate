# Define the PCIC models selected for best simulation of western North America
pcic12 = [dict(model=x.split()[0], run=x.split()[1]) for x in '''MPI-ESM-LR r3i1p1
inmcm4 r1i1p1
HadGEM2-ES r1i1p1
CanESM2 r1i1p1
MIROC5 r3i1p1
CSIRO-Mk3-6-0 r1i1p1
MRI-CGCM3 r1i1p1
ACCESS1-0 r1i1p1
CNRM-CM5 r1i1p1
CCSM4 r2i1p1
HadGEM2-CC r1i1p1
GFDL-ESM2G r1i1p1'''.split('\n')]
