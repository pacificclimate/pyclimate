import os

class Cmip5File():

    def __init__(self, fp):
        '''
        Parses a PCIC CMIP5 file path to extract specific metadata.
        Pattern is "<base_dir>/<institue>/<model>/<experiment>/<frequency>/<modeling realm>/<MIP table>/<ensemble member>/<version>/<variable name>/<CMOR filename>.nc"
                        -11       -10       -9        -8           -7            -6             -5           -4              -3           -2              -1
        CMOR filename is of pattern <variable_name>_<MIP table>_<model>_<experiment>_<ensemble member>_<temporal subset>.nc
                                           1             2         3         4               5                  6
        ex: root_dir/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/tasmax/tasmax_day_CanCM4_historical_r1i1p1_19610101-20051231.nc
        '''

        dirname, basename = os.path.split(os.path.abspath(fp))
        splitdirs = dirname.split('/')
        self.inst, self.model, self.experiment, self.freq, self.realm, self.mip, self.run, self.version, self.variable = splitdirs[-9:]
        self.root = os.path.join(*splitdirs[:-9])
        self.trange = basename.split('_')[-1]

    def __str__(self):
        return self.fullpath

    def __repr__(self):
        return "{}('{}')".format(self.__class__, self.fullpath)

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