import os
import fnmatch

from collections import defaultdict

from cfmeta import Cmip5File
from pyclimate.filters import Filter
from pyclimate.variables import DerivableBase


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


def iter_matching_cmip5_file(file_iter, _filter=None):

    # Instantiate filter
    _filter = Filter(_filter)

    for fp in file_iter:
        if fp in _filter:
            yield fp


def group_files_by_model_set(file_iter):

    model_sets = defaultdict(dict)
    for fp in file_iter:
        cf = Cmip5File(datanode_fp = fp)
        key = '{}_{}_{}_{}-{}'.format(cf.model, cf.experiment, cf.ensemble_member, cf.t_start, cf.t_end)

        if key not in model_sets:
            model_sets[key] = DerivableBase(**{k: cf.__dict__[k] for k in ('institute', 'model', 'experiment', 'frequency', 'modeling_realm', 'mip_table', 'ensemble_member', 'version_number', 'temporal_subset')})

        model_sets[key].add_base_variable(cf.variable_name, fp)

    return model_sets
