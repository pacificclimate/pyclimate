#!/usr/bin/env python

import os
import sys
import logging
import argparse

import numpy as np
from netCDF4 import Dataset

from pyclimate import Cmip5File, model_run_filter, iter_matching_cmip5_file
from pyclimate.nchelpers import *

log = logging.getLogger(__name__)


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

    return nc, ncvar

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

    return nc, ncvar

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

    return nc, ncvar

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

    return nc, ncvar

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

    return nc, ncvar

def derive(var_set, outdir, variables):

    do_tas = 'tas' in variables
    do_gdd = 'gdd' in variables
    do_hdd = 'hdd' in variables
    do_ffd = 'ffd' in variables
    do_pas = 'pas' in variables

    nc_tasmax = Dataset(var_set['tasmax'].fullpath)
    nc_tasmin = Dataset(var_set['tasmin'].fullpath)
    nc_pr = Dataset(var_set['pr'].fullpath)

    var_tasmax = nc_tasmax.variables['tasmax']
    var_tasmin = nc_tasmin.variables['tasmin']
    var_pr = nc_pr.variables['pr']
    assert var_tasmax.shape == var_tasmin.shape

    if do_tas:
        nc_tas, ncvar_tas = setup_tas(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    if do_gdd:
        nc_gdd, ncvar_gdd = setup_gdd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    if do_hdd:
        nc_hdd, ncvar_hdd = setup_hdd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    if do_ffd:
        nc_ffd, ncvar_ffd = setup_ffd(nc_tasmax, var_set['tasmax'].__dict__, outdir)

    if do_pas:
        nc_pas, ncvar_pas = setup_pas(nc_pr, var_set['tasmax'].__dict__, outdir)

    count = float(var_tasmax.shape[0])
    for i in range(var_tasmax.shape[0]):
        sys.stdout.write("\r{:.2%}".format(i/count))

        if do_tas:
            ncvar_tas[i,:,:] = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
        if do_gdd:
            if do_tas:
                ncvar_gdd[i,:,:] = np.where(ncvar_tas[i,:,:] > 278.15, (ncvar_tas[i,:,:] - 278.15), 0)
            else:
                tas = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
                ncvar_gdd[i,:,:] = np.where(tas > 278.15, (tas - 278.15), 0)
        if do_hdd:
            if do_tas:
                ncvar_hdd[i,:,:] = np.where(ncvar_tas[i,:,:] < 291.15, np.absolute(ncvar_tas[i,:,:] - 291.15), 0)
            else:
                tas = (var_tasmax[i,:,:] + var_tasmin[i,:,:]) / 2
                ncvar_hdd[i,:,:] = np.where(tas < 291.15, np.absolute(tas - 291.15), 0)
        if do_ffd:
            ncvar_ffd[i,:,:] = np.where(var_tasmin[i,:,:] > 273.15, 1, 0)
        if do_pas:
            ncvar_pas[i,:,:] = np.where(var_tasmax[i,:,:] < 273.15, var_pr[i,:,:] , 0)

def main(args):
    base_dir = args.indir
    log.info('Getting file list')
    file_iter = iter_matching_cmip5_file(base_dir, args.filter)

    log.info('Determining valid model sets')
    model_sets = group_files_by_model_set(file_iter)
            
    log.info(model_sets)

    exit()
        
    for i in range(len(model_sets)):
        log.info("[{}/{}]".format(i, len(model_sets)))
        derive(model_sets[i], args.outdir, args.variable)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', help='Input directory')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('-v', '--variable', nargs= '+',
                        choices=['tas', 'gdd', 'hdd', 'ffd', 'pas'],
                        help='Variable(s) to calculate. Ex: -v var1 var2 var3')
    parser.add_argument('-f', '--filter', help='Predefined model set to restrict file input to')
    parser.add_argument('--progress', default=False, action='store_true', help='Display percentage progress')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
