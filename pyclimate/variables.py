import os
import warnings

import numpy as np
from netCDF4 import Dataset

from cfmeta import Cmip5File
from pyclimate.nchelpers import nc_copy_atts, nc_copy_var

class DerivableBase(object):
    """Reprents a group of base variables.

    Grouped base variables are used to initiate calculating derived variables.

    Attributes:
        model (str): Model name. Typically the model_id attribute from the source NetCDF
        experiment (str): Experiment name. Typically the 'experiment' attribute from a source NetCDF
            eg: 'historical', 'rcp26'
        ensemble_member (str): Ensemble member id.
            eg: 'r1i1p1', r2i1p1'
        trange (str): Temporal range of data contained in the base data. Format YYYYMMDD-YYYYMMDD
            eg: '20060101-21991231'
    """
    required_atts = ['model', 'experiment', 'ensemble_member', 'temporal_subset']

    def __init__(self, **kwargs):
        """Initializes a `DerivableBase`

        Dynamically stores whatever args are supplied by a user.

        Args:
            **kwargs: Attributes defining `DerivableBase`

        Note:
            While not strictly enforced, `model`, `experiment`, `ensemble_member`, `temporal_subset` /should/
            be sufficient to uniquely group a set of variables. If required, a user can
            supply additional attributes to further define a grouping.
        """
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
        """Adds base variable to the DerivableBase instance.

        Args:
            variable (str): The CMIP5 variable name being added.
            dataset_fp (str): The location of the file.

        Returns:
            None
        """
        self.variables[variable] = dataset_fp

    def derive_variable(self, variable, outdir):
        """Entry point to calculate derived variables from a ``DerivableBase`` class.

        Args:
            variable (str): Short name of the variable to generate.
            outdir (str): Root directory to place output file.

        Returns:
            A variable specific subclass of DerivableBase.

        Raises:
            None.
        """
        if variable == 'tas':
            v = tas(self.variables, outdir)
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
        return v


def get_output_file_path_from_base(base_fp, new_varname, outdir=None):
    """Generates a new file path from an existing template using a different variable

    Args:
        base_fp (str): base filename to use as template
        new_varname (str): new variable name

    Returns:
        str: the new filename
    """
    cf = Cmip5File(datanode_fp = base_fp)
    cf.update(variable_name = new_varname)
    return os.path.join(outdir, cf.datanode_fp)

def get_output_netcdf_from_base(base_nc, base_varname, new_varname, new_atts, outfp):
    """Prepares a blank NetCDF file for a new variable

    Copies structure and attributes of an existing NetCDF into a new NetCDF
    alterting varialbe specific metadata

    Args:
        base_nc (netCDF4.Dataset): Source netCDF file as returned by netCDF4.Dataset.
        base_varname (str): Source variable to copy structure from.
        new_varname (str): New variable name.
        new_atts (dict): Attributes to assign to the new variable.
        out_fp (str): Location to create the new netCDF4.Dataset

    Returns:
        netCDF4.Dataset: The new netCDF4.Dataset
    """
    cf = Cmip5File(outfp)

    if not os.path.exists(os.path.dirname(outfp)):
        os.makedirs(os.path.dirname(outfp))

    new_nc = Dataset(outfp, 'w')
    ncvar = nc_copy_var(base_nc, new_nc, base_varname, new_varname)
    nc_copy_atts(base_nc, new_nc) #copy global atts
    for k, v in new_atts.items():
        setattr(ncvar, k, v)

    return new_nc


class DerivedVariable(object):
    """Used as a parent for all derived variables.

    Stores variable specific information and provides common methods.
    
    Attributes:
        base_variables (dict): Dictionary mapping base variable name to file location.
            eg: {'pr': 'path/to/pr/variable.nc',
                 'tasmax': 'path/to/tasmax/variable.nc'}
        outdir (str): Location to put the generated NetCDF.
        variable_name (str): Derived variable name.
        required_vars (list): List of variables required by the specific derived variable
        variable_atts (dict): Attributes to set on the derived variable
    """

    def __init__(self, base_variables, outdir, variable_name, required_vars, variable_atts):
        """Initializes a ``DerivedVariable`` class

        Args:
            Same as ``Attributes``

        """
        self.base_variables = base_variables
        self.outdir = outdir
        self.variable_name = variable_name
        self.required_vars = required_vars
        self.variable_atts = variable_atts

    def __call__(self):
        """__call__ method should be overridden by a child class
        """
        raise NotImplemented

    def __str__(self):
        return 'Generating {} with base variables {}'.format(type(self).__name__, self.base_variables.keys())

    @property
    def base_varname(self):
        """Used to set which base variable to use as a template.
        """
        return self.required_vars[0]

    @property
    def outfp(self): 
        """Generates a string
        """
        return get_output_file_path_from_base(self.base_variables[self.base_varname], self.variable_name, self.outdir)

    def has_required_vars(self, required_vars):
        if not all([x in self.base_variables.keys() for x in required_vars]):
            warnings.warn('Insufficient base variables to calculate {}'.format(self.variable_name))
            return False
        return True


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

    def __init__(self, base_variables, outdir):
        super(tas, self).__init__(base_variables, outdir, self.variable_name, self.required_vars, self.variable_atts)

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, self.outfp)
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

    def __init__(self, base_variables, outdir):
        super(gdd, self).__init__(base_variables, outdir, self.variable_name, self.required_vars, self.variable_atts)

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, self.outfp)
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

    def __init__(self, base_variables, outdir):
        super(hdd, self).__init__(base_variables, outdir, self.variable_name, self.required_vars, self.variable_atts)

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, self.outfp)
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

    def __init__(self, base_variables, outdir):
        super(ffd, self).__init__(base_variables, outdir, self.variable_name, self.required_vars, self.variable_atts)

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmin = Dataset(self.base_variables['tasmin'])
        var_tasmin = nc_tasmin.variables['tasmin']

        nc_out = get_output_netcdf_from_base(nc_tasmin, self.base_varname, self.variable_name, self.variable_atts, self.outfp)
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

    def __init__(self, base_variables, outdir):
        super(pas, self).__init__(base_variables, outdir, self.variable_name, self.required_vars, self.variable_atts)

    def __call__(self):
        if not self.has_required_vars(self.required_vars):
            return 1

        nc_tasmax = Dataset(self.base_variables['tasmax'])
        var_tasmax = nc_tasmax.variables['tasmax']

        nc_pr = Dataset(self.base_variables['pr'])
        var_pr = nc_pr.variables['pr']

        nc_out = get_output_netcdf_from_base(nc_tasmax, self.base_varname, self.variable_name, self.variable_atts, self.outfp)
        ncvar_pas = nc_out.variables[self.variable_name]

        for i in range(var_tasmax.shape[0]):
            ncvar_pas[i,:,:] = np.where(var_tasmax[i,:,:] < 273.15, var_pr[i,:,:] , 0)

        for nc in [nc_out, nc_tasmax]:
            nc.close()

        return 0
