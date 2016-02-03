import os
import warnings

import numpy as np
from netCDF4 import Dataset

from pyclimate import Cmip5File
from pyclimate.nchelpers import nc_copy_atts, nc_copy_var

class DerivableBase(object):
    required_atts = ['model', 'experiment', 'run', 'trange']

    def __init__(self, **kwargs):
        for att in self.required_atts:
            try:
                v = kwargs.pop(att)
                setattr(self, att, v)
            except KeyError:
                raise KeyError('Required attribute {} not provided'.format(att))
        if len(kwargs) != 0:
            for k, v in kwargs.items():
                setattr(self, k, v)

        self.variables = {}

    def add_base_variable(self, variable, dataset_fp):
        self.variables[variable] = dataset_fp

    def derive_variable(self, variable, outdir):
        print 'deriving var {}'.format(variable)
        if variable == 'tas':
            t = tas(self.variables, outdir)
        elif variable == 'gdd':
            v = gdd(self.variables, outdir)
        elif variable == 'hdd':
            v = hdd(self.variables, outdir)
        elif variable == 'ffd':
            v = ffd(self.variables, outdir)
        elif variable == 'pas':
            v = pas(self.variables, outdir)
        else:
            return None
        return v()


class DerivedVariable(object):
    # variable_name = ''
    # required_vars = []
    # variable_atts = {}

    def __init__(self, base_variables, outdir):
        self.base_variables = base_variables
        self.outdir = outdir

    def __call__(self):
        raise NotImplemented

    def has_required_vars(self, required_vars):
        if not all([x in self.base_variables.keys() for x in required_vars]):
            warnings.warn('Insufficient base variables to calculate {}'.format(self.variable_name))
            return False
        return True

    @property
    def base_varname(self):
        return self.required_vars[0]


def get_output_file_path_from_base(base_fp, new_varname, outdir=None):
    cf = Cmip5File(base_fp)
    cf.variable = new_varname
    if outdir:
        cf.root = outdir
    return cf.fullpath


def get_output_netcdf_from_base(base_nc, base_varname, new_varname, new_atts, outfp):
    cf = Cmip5File(outfp)

    if not os.path.exists(cf.dirname):
        os.makedirs(cf.dirname)

    new_nc = Dataset(outfp, 'w')
    ncvar = nc_copy_var(base_nc, new_nc, base_varname, new_varname)
    nc_copy_atts(base_nc, new_nc) #copy global atts
    for k, v in new_atts.items():
        setattr(ncvar, k, v)

    return new_nc


class tas(DerivedVariable):
    variable_name = 'tas'
    required_vars = ['tasmax', 'tasmin']
    variable_atts = {
        'long_name': 'Near-Surface Air Temperature',
        'standard_name': 'air_temperature',
        'units': 'K',
        'cell_methods': 'time: mean',
        'cell_measures': 'area: areacella'
    }

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        outfp = get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)
        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, outfp)
        ncvar_tas = nc_out.variables[self.variable_name]

        for i in range(var_tasmax.shape[0]):
            ncvar_tas[i,:,:] = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2

        for nc in [nc_out, nc_tasmax, nc_tasmin]:
            nc.close()

        return 0

class gdd(DerivedVariable):
    variable_name = 'gdd'
    required_vars = ['tasmax', 'tasmin']
    variable_atts = {
        'units': 'degree days',
        'long_name': 'Growing Degree Days'
    }

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        outfp = get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)
        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, outfp)
        ncvar_gdd = nc_out.variables[self.variable_name]

        for i in range(var_tasmax.shape[0]):
            tas = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
            ncvar_gdd[i,:,:] = np.where(tas > 278.15, (tas - 278.15), 0)

        for nc in [nc_out, nc_tasmax, nc_tasmin]:
            nc.close()

        return 0


class hdd(DerivedVariable):
    variable_name = 'hdd'
    required_vars = ['tasmax', 'tasmin']
    variable_atts = {
        'units': 'degree days',
        'long_name': 'Heating Degree Days'
    }

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        outfp = get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)
        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, outfp)
        ncvar_hdd = nc_out.variables[self.variable_name]

        for i in range(var_tasmax.shape[0]):
            tas = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
            ncvar_hdd[i,:,:] = np.where(tas < 291.15, np.absolute(tas - 291.15), 0)

        for nc in [nc_out, nc_tasmax, nc_tasmin]:
            nc.close()

        return 0


class ffd(DerivedVariable):
    variable_name = 'ffd'
    required_vars = ['tasmin']
    variable_atts = {
        'units': 'days',
        'long_name': 'Frost Free Days'
    }

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        outfp = get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)
        nc_out = get_output_netcdf_from_base(nc_tasmin, self.base_varname, self.variable_name, self.variable_atts, outfp)
        ncvar_ffd = nc_out.variables[self.variable_name]

        for i in range(var_tasmin.shape[0]):
            ncvar_ffd[i,:,:] = np.where(var_tasmin[i,:,:] > 273.15, 1, 0)

        for nc in [nc_out, nc_tasmin]:
            nc.close()

        return 0


class pas(DerivedVariable):
    variable_name = 'pas'
    required_vars = ['tasmax', 'pr']
    variable_atts = {
        'units': 'mm',
        'long_name': 'Precip as snow'
    }

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_pr = Dataset(self.base_variables['pr'])
        var_pr = nc_pr.variables['pr']

        outfp = get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)
        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, outfp)
        ncvar_pas = nc_out.variables[self.variable_name]

        for i in range(var_tasmax.shape[0]):
            ncvar_pas[i,:,:] = np.where(var_tasmax[i,:,:] < 273.15, var_pr[i,:,:] , 0)

        for nc in [nc_out, nc_tasmax]:
            nc.close()

        return 0
