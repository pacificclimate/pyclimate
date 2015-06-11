import logging

from netCDF4 import num2date

log = logging.getLogger(__name__)

def get_monthly_time_slices(ncvar_time):
    '''
    Based on an input NetCDF4 time variable returns calendar appropriate monthly slices
    '''
    assert 'calendar' in ncvar_time.ncattrs(), "Time variable does not have a defined calendar"
    cal = ncvar_time.calendar

    assert 'units' in ncvar_time.ncattrs(), "Time variable must have 'unit' attribute"
    units = ncvar_time.units

    assert len(ncvar_time.dimensions) == 1, "Time varaible must be single dimension"

    slices = []

    d_start = num2date(ncvar_time[0], units, cal)
    current_month = d_start.month
    t_start = 0
    for i, val in enumerate(ncvar_time):
        d = num2date(val, units, cal)
        if d.month != current_month:
            slices.append(slice(t_start, i))
            t_start = i
            current_month = d.month
    slices.append(slice(t_start, i+1))

    return slices


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

def nc_copy_dim(dsin, dsout, dimname):
    '''
    Copy a named dimension from an input file to an output file
    '''

    dim = dsin.dimensions[dimname]
    dsout.createDimension(dimname, len(dim) if not dim.isunlimited() else None)
    log.debug('Created dimension {}'.format(dimname))
    if dimname in dsin.variables:
        log.debug('Copying dimvar for {}'.format(dimname))
        nc_copy_var(dsin, dsout, dimname, dimname, copy_data=True, copy_attrs=True)

def nc_copy_var(dsin, dsout, varin, varout, copy_data=False, copy_attrs=False):
    '''
    Copies a variable from one NetCDF to another with dimensions, dimvars, and attributes
    '''

    log.debug('nc_copy_var: Copying variable {} to {}'.format(varin, varout))
    for dim in dsin.variables[varin].dimensions:
        if dim not in dsout.dimensions:
            nc_copy_dim(dsin, dsout, dim)

    if varout in dsout.variables.keys():
        # Avoid attempting to copy the dimvar twice. copy_var -> copy_dim -> copy_(dim)var = failure
        return

    ncvarin = dsin.variables[varin]
    fv = ncvarin._FillValue if ncvarin._FillValue else None
    ncvarout = dsout.createVariable(varout, ncvarin.datatype, ncvarin.dimensions, fill_value = fv)

    if 'bounds' in ncvarin.ncattrs():
        log.debug('found bounds: {}'.format(ncvarin.getncattr('bounds')))
        nc_copy_var(dsin, dsout, ncvarin.getncattr('bounds'), ncvarin.getncattr('bounds'), copy_data=True, copy_attrs=True)

    if copy_attrs:
        nc_copy_atts(dsin, dsout, varin, varout)
    if copy_data:
        if len(ncvarin.dimensions) > 3:
            raise AssertionError('This function does not support copying data for a variable with 4+ dimensions')
        # Itteratively copy data if 3 dimensions
        if len(ncvarin.shape) > 2:
            for i in range(ncvarin.shape[0]):
                ncvarout[i,:,:] = ncvarin[i,:,:]
        log.debug('Copied variable data')

    log.debug('Done copying variable')
    return ncvarout
