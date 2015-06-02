import logging

log = logging.getLogger(__name__)

def nc_copy_atts(dsin, dsout, varin=False, varout=False):
    '''
    Copy netcdf variable attributes. If varin = False, global attritubes are copied
    '''

    if varin:
        if varin not in dsin.variables or varout not in dsout.variables:
            raise KeyError("Unable to copy attributes. Varible does not exist in source or destination dataset")
        dsout.variables[varout].setncatts({k: dsin.variables[varin].getncattr(k) for k in dsin.variables[varin].ncattrs()})
        log.debug('Copied attributes from variable {} to variable {}'.format(varin, varout))

    else:
        dsout.setncatts({k: dsin.getncattr(k) for k in dsin.ncattrs()})
        log.debug('Copied global attributes')

def nc_copy_dimvar(dsin, dsout, varname):
    '''
    Naively copies a variable and its data. Suitable only for dimvars.
    Searches for and also copies dimvar bounds if it exists
    '''

    invar = dsin.variables[varname]
    outvar = dsout.createVariable(varname, invar.datatype, invar.dimensions)
    nc_copy_atts(dsin, dsout, varname, varname)
    outvar[:] = invar[:]
    log.debug('Copied dimvar {}'.format(varname))

    if 'bounds' in invar.ncattrs():
        log.debug('found bounds: {}'.format(outvar.getncattr('bounds')))
        nc_copy_var(dsin, dsout, invar.getncattr('bounds'), outvar.getncattr('bounds'), copy_data=True)

def nc_copy_dim(dsin, dsout, dimname):
    '''
    Copy a named dimension from an input file to an output file
    '''

    dim = dsin.dimensions[dimname]
    dsout.createDimension(dimname, len(dim) if not dim.isunlimited() else None)
    log.debug('Created dimension {}'.format(dimname))

def nc_copy_variable_dimensions(dsin, dsout, varin, varout):
    '''
    Copies all dimensions (and dimvars) defining variable
    '''

    dims = dsin.variables[varin].dimensions
    for dim in dims:
        if dim not in dsout.dimensions:
            nc_copy_dim(dsin, dsout, dim)
            if dim in dsin.variables:
                log.debug('Copying dimvar for {}'.format(dim))
                nc_copy_dimvar(dsin, dsout, dim)

def nc_copy_var(dsin, dsout, varin, varout, copy_data=False, copy_attrs=False):
    '''
    Copies a variable from one NetCDF to another with dimensions, dimvars, and attributes
    '''

    nc_copy_variable_dimensions(dsin, dsout, varin, varout)
    ncvarin = dsin.variables[varin]
    ncvarout = dsout.createVariable(varout, ncvarin.datatype, ncvarin.dimensions)
    if copy_attrs:
        nc_copy_atts(dsin, dsout, varin, varout)
    if copy_data:
        ncvarout[:] = ncvarin[:]
        log.debug('Copied variable data')
        
    return ncvarout
