import logging
import ast

from pyclimate import Cmip5File

'''
A filter is a list of dictionaries. Each dictionary is keyed to Cmip5File attributes
with either a scalar or list as acceptable value(s)

Examples:
    A simple filter would indicate only CanESM2 r1i1p1 models are desired.
    [
        { 'model': 'CanEMS2' }
    ]

    This filter would apply an OR between dictionaries, AND within dictionary key
    value pairs, and OR within dictionary values if they are a list

    [
        { 'model': 'CanEMS2', 'run': [ 'r1i1p1', 'r2i1p1' ] },
        { 'model': 'HadGEM2-CC', 'run': 'r1i1p1' } 
    ]

'''

log = logging.getLogger(__name__)

# class FilterMetaclass(type):

#     def __new__(cls, clsname, bases, dct):
#         print(dct)
#         return super(FilterMetaclass, cls).__new__(cls, clsname, bases, dct)

#     def __init__(cls, clsname, bases, dct):
#         print(dct)

class Filter(object):
#     __metaclass__ = FilterMetaclass

    def __init__(self, _filter=None):
        preset = get_preset_filter('pcic12')
        if preset:
            self.filter = preset
        else:
            try:
                self.filter = ast.literal_eval(_filter)
            except Exception as e:
                raise Exception('Unable to convert filter to python list of dictionaries')

    def __contains__(self, fp):
        '''
        Returns true if a file path is included in a filter
        '''
        if not self.filter: return True

        cf = Cmip5File(fp)
        for entry in self.filter:
            if all([(hasattr(cf, att) and (getattr(cf, att) == val or getattr(cf, att) in val)) for att, val in entry.items()]):
                return True

        return False

def get_preset_filter(_filter):
    if _filter in presets.keys():
        return presets[_filter]
    else:
        return None


presets= {'pcic12': [{'model': x.split()[0], 'run': x.split()[1], 'experiment': x.split()[2:]} for x in '''MPI-ESM-LR r3i1p1 historical rcp26 rcp45 rcp85
inmcm4 r1i1p1 historical rcp26 rcp45 rcp85
HadGEM2-ES r1i1p1 historical rcp26 rcp45 rcp85
CanESM2 r1i1p1 historical rcp26 rcp45 rcp85
MIROC5 r3i1p1 historical rcp26 rcp45 rcp85
CSIRO-Mk3-6-0 r1i1p1 historical rcp26 rcp45 rcp85
MRI-CGCM3 r1i1p1 historical rcp26 rcp45 rcp85
ACCESS1-0 r1i1p1 historical rcp26 rcp45 rcp85
CNRM-CM5 r1i1p1 historical rcp26 rcp45 rcp85
CCSM4 r2i1p1 historical rcp26 rcp45 rcp85
HadGEM2-CC r1i1p1 historical rcp26 rcp45 rcp85
GFDL-ESM2G r1i1p1 historical rcp26 rcp45 rcp85'''.split('\n')]}
