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


def main(args):
    base_dir = args.indir
    log.info('Getting file list')
    netcdf_iter = iter_netcdf_files(base_dir)
    file_iter = iter_matching_cmip5_file(netcdf_iter, args.filter)

    log.info('Determining valid model sets')
    model_sets = group_files_by_model_set(file_iter)

    log.info(model_sets)

    for k, base in model_sets.items():
        for variable in args.variable:
            base.derive_variable(variable, args.outdir)
            exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--indir', help='Input directory')
    parser.add_argument('-o', '--outdir', help='Output directory')
    parser.add_argument('-v', '--variable', nargs= '+',
                        choices=['tas', 'gdd', 'hdd', 'ffd', 'pas'],
                        help='Variable(s) to calculate. Ex: -v var1 var2 var3')
    parser.add_argument('-f', '--filter', help='Predefined model set to restrict file input to')
    parser.add_argument('--progress', default=False, action='store_true', help='Display percentage progress')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
