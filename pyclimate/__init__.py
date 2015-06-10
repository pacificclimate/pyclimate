import os

from collections import defaultdict

class Cmip5File():

    def __init__(self, fp=None, **kwargs):
        '''
        Parses or builds a PCIC CMIP5 file path with specific metadata.
        Pattern is "<base_dir>/<institue>/<model>/<experiment>/<frequency>/<modeling realm>/<CMOR table>/<ensemble member>/<version>/<variable name>/<CMOR filename>.nc"
                        -11       -10       -9        -8           -7            -6             -5           -4              -3           -2              -1
        CMOR filename is of pattern <variable_name>_<CMOR table>_<model>_<experiment>_<ensemble member>_<temporal subset>.nc
                                           1             2         3         4               5                  6
        ex: root_dir/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/tasmax/tasmax_day_CanCM4_historical_r1i1p1_19610101-20051231.nc

        Metadata requirements are found: http://cmip-pcmdi.llnl.gov/cmip5/docs/CMIP5_output_metadata_requirements.pdf
        Data Reference Syntax: http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
        Standard Output (CMOR Tables): http://cmip-pcmdi.llnl.gov/cmip5/docs/standard_output.pdf
        '''

        if fp:
            dirname, basename = os.path.split(os.path.abspath(fp))
            splitdirs = dirname.split('/')
            self.inst, self.model, self.experiment, self.freq, self.realm, self.mip, self.run, self.version, self.variable = splitdirs[-9:]
            self.root = os.path.join(*splitdirs[:-9])
            self.trange = basename.split('_')[-1]

        else:
            required_meta = ['institute', 'model', 'experiment', 'freq', 'realm', 'mip', 'run', 'version', 'variable', 'trange']
            for att in required_meta:
                try:
                    setattr(self, att, kwargs[att])
                except KeyError:
                    raise KeyError('Required attribute {} not provided'.format(att))

    def __str__(self):
        return self.fullpath

    def __repr__(self):
        return "{}('{}')".format(self.__class__, self.__dict__)

    @property
    def basename(self):
        return '_'.join([self.variable, self.mip, self.model, self.experiment, self.run, self.trange])

    @property
    def dirname(self, root=None):
        if not root: root = self.root
        return os.path.join('/', root, self.inst, self.model, self.experiment, self.freq, self.realm, self.mip, self.run, self.version, self.variable)

    @property
    def fullpath(self):
        return os.path.join(self.dirname, self.basename)

    @property
    def t_start(self):
        return self.trange.split('-')[0]

    @t_start.setter
    def t_start(self, value):
        self.trange = '-'.join(value, self.trange.split('-')[1])

    @property
    def t_end(self):
        return self.trange.split('-')[1]

    @t_end.setter
    def t_end(self, value):
        self.trange = '-'.join(self.trange.split('-')[1], value)

    @property
    def cmip3_basename(self):
        return '-'.join([self.model, self.experiment, self.variable, self.run])

    @property
    def cmip3_dirname(self, root=None):
        if not root: root = self.root
        return os.path.join('/', root, self.experiment, self.variable, self.model, self.run)

    @property
    def cmip3_fullpath(self):
        return os.path.join(self.dirname, self.basename)


class Cmip3File():

    def __init__(self, fp=None, **kwargs):
        '''
        Parses or builds a PCIC CMIP3 file path with specific metadata.
        Pattern is "<base_dir>/<experiment>/<variable name>/<model>/<ensemble member>/<filename>.nc"
                        -6         -5            -4           -3           -2              -1
        Filename is of pattern <model>-<experiment>-<variable name>-<ensemble memter>.nc
                                  1         2              3                4
        ex: root_dir/rcp45/tasmax/ACCESS1-3/r1i1p1/ACCESS1-3-rcp45-tasmax-r1i1p1.nc

        Metadata requirements are found here: http://www-pcmdi.llnl.gov/ipcc/IPCC_output_requirements.htm
        '''

        if fp:
            dirname, basename = os.path.split(os.path.abspath(fp))
            splitdirs = dirname.split('/')
            self.experiment, self.variable, self.model, self.run = splitdirs[-4:]
            self.root = os.path.join(*splitdirs[:-4])

        else:
            required_meta = ['model', 'experiment', 'run', 'variable']
            for att in required_meta:
                try:
                    setattr(self, att, kwargs[att])
                except KeyError:
                    raise KeyError('Required attribute {} not provided'.format(att))

    def __str__(self):
        return self.fullpath

    def __repr__(self):
        return "{}('{}')".format(self.__class__, self.__dict__)

    @property
    def basename(self):
        return '-'.join([self.model, self.experiment, self.variable, self.run])

    @property
    def dirname(self, root=None):
        if not root: root = self.root
        return os.path.join('/', root, self.experiment, self.variable, self.model, self.run)

    @property
    def fullpath(self):
        return os.path.join(self.dirname, self.basename)


def model_run_filter(fpath, valid_model_runs):
    '''
    Determines if a file path is within the provided filter
    '''
    cf = Cmip5File(fpath)
    if cf.model in valid_model_runs.keys() and cf.run in valid_model_runs[cf.model]:
        return True
    return False


def get_model_set(set_name):
    '''
    Returns a nested dict of model/run combinations for predefined sets
    '''

    if set_name == 'pcic12':
    # Define the PCIC models selected for best simulation of western North America
        d = defaultdict(list)
        valid_runs = [(x.split()[0], x.split()[1]) for x in '''MPI-ESM-LR r3i1p1
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
        for model, run in valid_runs:
            d[model].append(run)
        return d
