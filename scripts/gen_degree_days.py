#!/usr/bin/env python

import os
import sys
import fnmatch
import logging
import argparse

import numpy as np
from netCDF4 import Dataset

from pyclimate import Cmip5File, model_run_filter, get_model_set
from pyclimate.nchelpers import *

log = logging.getLogger(__name__)

def get_recursive_file_list(base_dir, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

def setup_tas(nc_source, d, outdir):

    tas = Cmip5File(**d)
    tas.variable = 'tas'
    tas.root = outdir
    if not os.path.exists(tas.dirname):
        os.makedirs(tas.dirname)

    nc = Dataset(tas.fullpath, 'w')
    ncvar = nc_copy_var(nc_source, nc, 'tasmax', 'tas', copy_attrs=True, copy_data=False)
    nc_copy_atts(nc_source, nc) #copy global atts
    ncvar.long_name = 'Near-Surface Air Temperature'
    ncvar.standard_name = 'air_temperature'
    ncvar.units = 'K'
    ncvar.cell_methods = 'time: mean'
    ncvar.cell_measures = 'area: areacella'

    return nc

def setup_gdd(nc_source, d, outdir):

    gdd = Cmip5File(**d)
    gdd.variable = 'gdd'
    gdd.root = outdir
    if not os.path.exists(gdd.dirname):
        os.makedirs(gdd.dirname)

    nc = Dataset(gdd.fullpath, 'w')
    ncvar = nc_copy_var(nc_source, nc, 'tasmax', 'gdd', copy_data=False)
    nc_copy_atts(nc_source, nc) #copy global atts
    ncvar.units = 'degree days'
    ncvar.long_name = 'Growing Degree Days'

    return nc

def setup_hdd(nc_source, d, outdir):

    hdd = Cmip5File(**d)
    hdd.variable = 'hdd'
    hdd.root = outdir
    if not os.path.exists(hdd.dirname):
        os.makedirs(hdd.dirname)

    nc = Dataset(hdd.fullpath, 'w')
    ncvar = nc_copy_var(nc_source, nc, 'tasmax', 'hdd', copy_data=False)
    nc_copy_atts(nc_source, nc) #copy global atts
    ncvar.units = 'degree days'
    ncvar.long_name = 'Heating Degree Days'

    return nc

def setup_ffd(nc_source, d, outdir):

    ffd = Cmip5File(**d)
    ffd.variable = 'ffd'
    ffd.root = outdir
    if not os.path.exists(ffd.dirname):
        os.makedirs(ffd.dirname)

    nc = Dataset(ffd.fullpath, 'w')
    ncvar = nc_copy_var(nc_source, nc, 'tasmax', 'ffd', copy_data=False)
    nc_copy_atts(nc_source, nc) #copy global atts
    ncvar.units = 'days'
    ncvar.long_name = 'Frost Free Days'

    return nc


def setup_pas(nc_source, d, outdir):

    pas = Cmip5File(**d)
    pas.variable = 'pas'
    pas.root = outdir
    if not os.path.exists(pas.dirname):
        os.makedirs(pas.dirname)

    nc = Dataset(pas.fullpath, 'w')
    ncvar = nc_copy_var(nc_source, nc, 'pr', 'pas', copy_data=False)
    nc_copy_atts(nc_source, nc) #copy global atts
    ncvar.units = 'days'
    ncvar.long_name = 'Frost Free Days'

    return nc

def calc_tas(var_set, outdir):
    nc_tasmax = Dataset(var_set['tasmax'].fullpath)
    nc_tasmin = Dataset(var_set['tasmin'].fullpath)
    nc_pr = Dataset(var_set['pr'].fullpath)

    var_tasmax = nc_tasmax.variables['tasmax']
    var_tasmin = nc_tasmin.variables['tasmin']
    var_pr = nc_pr.variables['pr']
    assert var_tasmax.shape == var_tasmin.shape

    # Set up tas
    nc_tas = setup_tas(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    # Set up gdd
    nc_gdd = setup_gdd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    # Set up hdd
    nc_hdd = setup_hdd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    # Set up ffd
    nc_ffd = setup_ffd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    # Set up pas
    nc_pas = setup_pas(nc_pr, var_set['tasmax'].__dict__, outdir)


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
