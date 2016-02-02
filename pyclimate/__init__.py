import os
import fnmatch
import multiprocessing

from collections import defaultdict

from variables import DerivableBase

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
            self.institute, self.model, self.experiment, self.freq, self.realm, self.mip, self.run, self.version, self.variable = splitdirs[-9:]
            self.root = os.path.join(*splitdirs[:-9])
            self.trange = os.path.splitext(basename)[0].split('_')[-1]

        else:
            required_meta = ['institute', 'model', 'experiment', 'freq', 'realm', 'mip', 'run', 'version', 'variable', 'trange']
            for att in required_meta:
                try:
                    v = kwargs.pop(att)
                    setattr(self, att, v)
                except KeyError:
                    raise KeyError('Required attribute {} not provided'.format(att))
            if len(kwargs) != 0:
                for k, v in kwargs.items():
                    setattr(self, k, v)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.fullpath

    def __repr__(self):
        s = "Cmip5File("
        args = ", ".join(["{} = '{}'".format(k, v) for k, v in self.__dict__.items()])
        # if self.root:
        #     args += ", root = '{}'".format(self.root)
        s += args + ")"
        return s

    @property
    def basename(self):
        return '_'.join([self.variable, self.mip, self.model, self.experiment, self.run, self.trange]) + '.nc'

    @property
    def dirname(self, root=None):
        if not root: root = self.root
        return os.path.join('/', root, self.institute, self.model, self.experiment, self.freq, self.realm, self.mip, self.run, self.version, self.variable)

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
        return '-'.join([self.model, self.experiment, self.variable, self.run]) + '.nc'

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
                    v = kwargs.pop(att)
                    setattr(self, att, v)
                except KeyError:
                    raise KeyError('Required attribute {} not provided'.format(att))
            if len(kwargs) != 0:
                for k, v in kwargs.items():
                    setattr(self, k, v)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.fullpath

    def __repr__(self):
        s = "Cmip3File("
        args = ", ".join(["{} = '{}'".format(k, v) for k, v in self.__dict__.items()])
        # if self.root:
        #     args += ", root = '{}'".format(self.root)
        s += args + ")"
        return s

    @property
    def basename(self):
        return '-'.join([self.model, self.experiment, self.variable, self.run]) + '.nc'

    @property
    def dirname(self, root=None):
        if not root: root = self.root
        return os.path.join('/', root, self.experiment, self.variable, self.model, self.run)

    @property
    def fullpath(self):
        return os.path.join(self.dirname, self.basename)

class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison Pill says exit
                print '%s: Exiting' % proc_name
                break
            print '{}: {}'.format(proc_name, next_task)
            answer = next_task()
            self.result_queue.put(answer)
        return

def iter_netcdf_files(base_dir, pattern="*.nc"):
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)

def model_run_filter(fpath, valid_model_runs):
    '''
    Determines if a file path is within the provided filter
    '''
    cf = Cmip5File(fpath)
    if cf.model in valid_model_runs.keys() and cf.run in valid_model_runs[cf.model]:
        return True
    return False


from pyclimate.filters import Filter

def iter_matching_cmip5_file(file_iter, _filter=None):

    # Instantiate filter
    _filter = Filter(_filter)

    for fp in file_iter:
        if fp in _filter:
            yield fp



from collections import defaultdict

def group_files_by_model_set(file_iter):

    model_sets = defaultdict(dict)
    for fp in file_iter:
        cf = Cmip5File(fp)
        key = '{}_{}_{}_{}-{}'.format(cf.model, cf.experiment, cf.run, cf.t_start, cf.t_end)

        if key not in model_sets:
            model_sets[key] = DerivableBase(**{k: cf.__dict__[k] for k in ('institute', 'model', 'experiment', 'freq', 'realm', 'mip', 'run', 'version', 'variable', 'trange')})

        model_sets[key].add_base_variable(cf.variable, fp)

    return model_sets
