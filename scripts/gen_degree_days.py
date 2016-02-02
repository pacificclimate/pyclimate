#!/usr/bin/env python

import os
import sys
import logging
import argparse

import numpy as np
from netCDF4 import Dataset

from pyclimate import Cmip5File
from pyclimate.path import iter_netcdf_files, group_files_by_model_set, iter_matching_cmip5_file
from pyclimate.nchelpers import *

log = logging.getLogger(__name__)

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
    netcdf_iter = iter_netcdf_files(base_dir)
    file_iter = iter_matching_cmip5_file(netcdf_iter, args.filter)

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
