#!/usr/bin/env python

import os
import sys
import fnmatch
import logging
import argparse

import numpy as np
from netCDF4 import Dataset

from pyclimate.cmip5 import Cmip5File, model_run_filter
from pyclimate.nchelpers import *
from pyclimate import get_model_set

log = logging.getLogger(__name__)

def get_recursive_file_list(base_dir, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

def calc_tas(var_set, outdir):
    nc_tasmax = Dataset(var_set['tasmax'].fullpath)
    nc_tasmin = Dataset(var_set['tasmin'].fullpath)
    nc_pr = Dataset(var_set['pr'].fullpath)
    
    var_tasmax = nc_tasmax.variables['tasmax']
    var_tasmin = nc_tasmin.variables['tasmin']
    var_pr = nc_pr.variables['pr']
    assert var_tasmax.shape == var_tasmin.shape

    # Set up tas
    tas = Cmip5File((var_set['tasmax'].fullpath))
    tas.variable = 'tas'
    tas.root = outdir
    if not os.path.exists(tas.dirname):
        os.makedirs(tas.dirname)

    tas.nc = Dataset(tas.fullpath, 'w')
    tas.ncvar = nc_copy_var(nc_tasmax, tas.nc, 'tasmax', 'tas', copy_data=False)
    nc_copy_atts(nc_tasmax, tas.nc) #copy global atts
    tas.ncvar.long_name = 'Near-Surface Air Temperature'
    tas.ncvar.standard_name = 'air_temperature'
    tas.ncvar.units = 'K'
    tas.ncvar.cell_methods = 'time: mean'
    tas.ncvar.cell_measures = 'area: areacella'
    tas.missing_value = 1e20
    tas._FillValue = 1e20

    # Set up gdd
    gdd = Cmip5File((var_set['tasmax'].fullpath))
    gdd.variable = 'gdd'
    gdd.root = outdir
    if not os.path.exists(gdd.dirname):
        os.makedirs(gdd.dirname)

    gdd.nc = Dataset(gdd.fullpath, 'w')
    gdd.ncvar = nc_copy_var(nc_tasmax, gdd.nc, 'tasmax', 'gdd', copy_data=False)
    nc_copy_atts(nc_tasmax, gdd.nc) #copy global atts
    gdd.ncvar.units = 'degree days'
    gdd.ncvar.long_name = 'Growing Degree Days'

    # Set up hdd
    hdd = Cmip5File((var_set['tasmax'].fullpath))
    hdd.variable = 'hdd'
    hdd.root = outdir
    if not os.path.exists(hdd.dirname):
        os.makedirs(hdd.dirname)

    hdd.nc = Dataset(hdd.fullpath, 'w')
    hdd.ncvar = nc_copy_var(nc_tasmax, hdd.nc, 'tasmax', 'hdd', copy_data=False)
    nc_copy_atts(nc_tasmax, hdd.nc) #copy global atts
    hdd.ncvar.units = 'degree days'
    hdd.ncvar.long_name = 'Heating Degree Days'

    # Set up ffd
    ffd = Cmip5File((var_set['tasmax'].fullpath))
    ffd.variable = 'ffd'
    ffd.root = outdir
    if not os.path.exists(ffd.dirname):
        os.makedirs(ffd.dirname)

    ffd.nc = Dataset(ffd.fullpath, 'w')
    ffd.ncvar = nc_copy_var(nc_tasmax, ffd.nc, 'tasmax', 'ffd', copy_data=False)
    nc_copy_atts(nc_tasmax, ffd.nc) #copy global atts
    ffd.ncvar.units = 'days'
    ffd.ncvar.long_name = 'Frost Free Days'

    # Set up pas
    pas = Cmip5File((var_set['tasmax'].fullpath))
    pas.variable = 'pas'
    pas.root = outdir
    if not os.path.exists(pas.dirname):
        os.makedirs(pas.dirname)

    pas.nc = Dataset(pas.fullpath, 'w')
    pas.ncvar = nc_copy_var(nc_pr, pas.nc, 'pr', 'pas', copy_data=False)
    nc_copy_atts(nc_pr, pas.nc) #copy global atts
    pas.ncvar.units = 'days'
    pas.ncvar.long_name = 'Frost Free Days'

    count = float(var_tasmax.shape[0])
    for i in range(var_tasmax.shape[0]):
        sys.stdout.write("\r{:.2%}".format(i/count))
        tas.ncvar[i,:,:] = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
        gdd.ncvar[i,:,:] = np.where(tas.ncvar[i,:,:] > 278.15, (tas.ncvar[i,:,:] - 278.15), 0)
        hdd.ncvar[i,:,:] = np.where(tas.ncvar[i,:,:] < 291.15, np.absolute(tas.ncvar[i,:,:] - 291.15), 0)
        ffd.ncvar[i,:,:] = np.where(var_tasmin[i,:,:] > 273.15, 1, 0)
        pas.ncvar[i,:,:] = np.where(var_tasmax[i,:,:] < 273.15, var_pr[i,:,:] , 0)

def main(args):
    base_dir = args.indir
    log.info('Getting file list')
    file_list = get_recursive_file_list(base_dir, '*.nc')
    log.info('Found {} netcdf files'.format(len(file_list)))

    if args.model_filter:
        log.info('Filtering to requested set')
        _filter = get_model_set(args.model_filter)
        file_list = [x for x in file_list if model_run_filter(x, _filter)]
        log.info('{} resulting files'.format(len(file_list)))

    log.info('Determining valid model sets')
    tasmax_files = [x for x in file_list if 'tasmax' in x]
    tasmin_files = [x.replace('tasmax', 'tasmin') for x in tasmax_files]
    tasmin_files_available = [x in file_list for x in tasmin_files]
    pr_files = [x.replace('tasmax', 'pr') for x in tasmax_files]
    pr_files_available = [x in file_list for x in pr_files]
    files_available = [all((x, y)) for x, y in zip(tasmin_files_available, pr_files_available)]

    log.info('Found {} tasmax, tasmin, pr model sets'.format(len(files_available)))

    model_sets = [{'tasmax': Cmip5File(tasmax), 'tasmin': Cmip5File(tasmin), 'pr': Cmip5File(pr)} for tasmax, tasmin, pr, file_available in zip(tasmax_files, tasmin_files, pr_files, files_available) if file_available]

    for i in range(len(model_sets)):
        log.info("[{}/{}]".format(i, len(model_sets)))
        model_sets['tas'] = calc_tas(model_sets[i], args.outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', help='Input directory')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('-v', '--variable', nargs= '+',  help='Variable(s) to calculate. Ex: -v var1 var2 var3')
    parser.add_argument('-m', '--model_filter', help='Predefined model set to restrict file input to')
    parser.add_argument('--progress', default=False, action='store_true', help='Display percentage progress')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
