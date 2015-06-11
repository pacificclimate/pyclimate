import os
import pytest

from tempfile import NamedTemporaryFile

import netCDF4
import numpy as np

def get_base_3d_nc(dims, calendar='standard', start_time = 0):
    f = NamedTemporaryFile(suffix='.nc')
    nc = netCDF4.Dataset(f.name, 'w')
    nc.model_id = 'test'
    nc.source = 'random data'

    lat = nc.createDimension('lat', dims['lat'])
    var_lat = nc.createVariable('lat', 'f4', 'lat')
    var_lat[:] = range(dims['lat'])

    var_lat.axis = 'Y'
    var_lat.units = 'degrees_north'
    var_lat.long_name = 'latitude'

    lon = nc.createDimension('lon', dims['lon'])
    var_lon = nc.createVariable('lon', 'f4', 'lon')
    var_lon[:] = range(dims['lon'])

    var_lon.axis = 'X'
    var_lon.units = 'degrees_east'
    var_lon.long_name = 'longitude'

    time = nc.createDimension('time', dims['time'])
    var_time = nc.createVariable('time', 'i4', 'time')
    var_time[:] = range(start_time, start_time + dims['time'])

    var_time.axis = 'T'
    var_time.units = 'days since 2000-01-01'
    var_time.calendar = calendar
    var_time.long_name = 'time'

    var = nc.createVariable('tasmax', 'f4', ('time', 'lat', 'lon'), fill_value=1e20)
    var.standard_name = "air_temperature"
    var.long_name = "Daily Maximum Near-Surface Air Temperature"
    var.units = 'K'
    var.missing_value = 1e20
    for t in range(dims['time']):
        var[t,:,:] = np.random.randn(dims['lat'], dims['lon'])

    return nc

@pytest.fixture(scope="session")
def nc_3d(request):
    nc = get_base_3d_nc({'time': 32, 'lon': 128, 'lat': 64})

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope="function")
def nc_3d_bare(request):
    f = NamedTemporaryFile()
    dims = {'time': 32, 'lon': 128, 'lat': 64}
    nc = netCDF4.Dataset(f.name, 'w')
    lat = nc.createDimension('lat', dims['lat'])
    lon = nc.createDimension('lon', dims['lon'])
    time = nc.createDimension('time', dims['time'])

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope='module')
def cmip5_file_list():
    fl = '''/root/directory/CCCMA/CanESM2/rcp85/day/atmos/day/r1i1p1/v20120407/tasmin/tasmin_day_CanESM2_rcp85_r1i1p1_20060101-21001231.nc
/root/directory/CCCMA/CanESM2/rcp85/day/atmos/day/r1i1p1/v20120407/pr/pr_day_CanESM2_rcp85_r1i1p1_20060101-21001231.nc
/root/directory/CCCMA/CanESM2/rcp85/day/atmos/day/r1i1p1/v20120407/tasmax/tasmax_day_CanESM2_rcp85_r1i1p1_20060101-21001231.nc
/root/directory/CCCMA/CanESM2/rcp45/day/atmos/day/r1i1p1/v20120410/tasmin/tasmin_day_CanESM2_rcp45_r1i1p1_20060101-23001231.nc
/root/directory/CCCMA/CanESM2/rcp45/day/atmos/day/r1i1p1/v20120410/tasmax/tasmax_day_CanESM2_rcp45_r1i1p1_20060101-23001231.nc
/root/directory/CCCMA/CanESM2/historical/day/atmos/day/r1i1p1/v20120410/pr/pr_day_CanESM2_historical_r1i1p1_18500101-20051231.nc
/root/directory/CCCMA/CanESM2/historical/day/atmos/day/r1i1p1/v20120410/tasmax/tasmax_day_CanESM2_historical_r1i1p1_18500101-20051231.nc
/root/directory/CCCMA/CanESM2/rcp26/day/atmos/day/r1i1p1/v20120410/tasmax/tasmax_day_CanESM2_rcp26_r1i1p1_20060101-23001231.nc
/root/directory/CCCMA/CanESM2/rcp26/day/atmos/day/r1i1p1/v20120410/pr/pr_day_CanESM2_rcp26_r1i1p1_20060101-23001231.nc
/root/directory/CCCMA/CanESM2/rcp26/day/atmos/day/r1i1p1/v20120410/tasmin/tasmin_day_CanESM2_rcp26_r1i1p1_20060101-23001231.nc
/root/directory/CCCMA/CanCM4/rcp45/day/atmos/day/r1i1p1/v20120612/pr/pr_day_CanCM4_rcp45_r1i1p1_20060101-20351231.nc
/root/directory/CCCMA/CanCM4/rcp45/day/atmos/day/r1i1p1/v20120612/tasmin/tasmin_day_CanCM4_rcp45_r1i1p1_20060101-20351231.nc
/root/directory/CCCMA/CanCM4/rcp45/day/atmos/day/r1i1p1/v20120612/tasmax/tasmax_day_CanCM4_rcp45_r1i1p1_20060101-20351231.nc
/root/directory/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/tasmin/tasmin_day_CanCM4_historical_r1i1p1_19610101-20051231.nc
/root/directory/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/tasmax/tasmax_day_CanCM4_historical_r1i1p1_19610101-20051231.nc
/root/directory/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/pr/pr_day_CanCM4_historical_r1i1p1_19610101-20051231.nc'''.split('\n')
    return fl

@pytest.fixture(scope='module')
def cmip5_file():
    fp = '/root/directory/CCCMA/CanESM2/rcp85/day/atmos/day/r1i1p1/v20120407/tasmin/tasmin_day_CanESM2_rcp85_r1i1p1_20060101-21001231.nc'
    return fp

@pytest.fixture(scope='module')
def cmip3_file_list():
    fl = '''/root/rcp45/tasmax/CanCM4/r1i1p1/CanCM4-rcp45-tasmax-r1i1p1.nc
/root/rcp45/tasmax/CanESM2/r1i1p1/CanESM2-rcp45-tasmax-r1i1p1.nc
/root/rcp45/pr/CanESM2/r1i1p1/CanESM2-rcp45-pr-r1i1p1.nc
/root/rcp45/pr/CanCM4/r1i1p1/CanCM4-rcp45-pr-r1i1p1.nc
/root/rcp45/tasmin/CanESM2/r1i1p1/CanESM2-rcp45-tasmin-r1i1p1.nc
/root/rcp45/tasmin/CanCM4/r1i1p1/CanCM4-rcp45-tasmin-r1i1p1.nc
/root/rcp26/pr/CanESM2/r1i1p1/CanESM2-rcp26-pr-r1i1p1.nc
/root/rcp26/tasmin/CanESM2/r1i1p1/CanESM2-rcp26-tasmin-r1i1p1.nc
/root/rcp26/tasmax/CanESM2/r1i1p1/CanESM2-rcp26-tasmax-r1i1p1.nc
/root/historical/tasmin/CanESM2/r1i1p1/CanESM2-historical-tasmin-r1i1p1.nc
/root/historical/tasmin/CanCM4/r1i1p1/CanCM4-historical-tasmin-r1i1p1.nc
/root/historical/tasmax/CanCM4/r1i1p1/CanCM4-historical-tasmax-r1i1p1.nc
/root/historical/tasmax/CanESM2/r1i1p1/CanESM2-historical-tasmax-r1i1p1.nc
/root/historical/pr/CanCM4/r1i1p1/CanCM4-historical-pr-r1i1p1.nc
/root/historical/pr/CanESM2/r1i1p1/CanESM2-historical-pr-r1i1p1.nc
/root/rcp85/tasmax/CanESM2/r1i1p1/CanESM2-rcp85-tasmax-r1i1p1.nc
/root/rcp85/tasmin/CanESM2/r1i1p1/CanESM2-rcp85-tasmin-r1i1p1.nc
/root/rcp85/pr/CanESM2/r1i1p1/CanESM2-rcp85-pr-r1i1p1.nc'''.split('\n')
    return fl

@pytest.fixture(scope='module')
def cmip3_file():
    fp = '/root/rcp45/tasmax/CanCM4/r1i1p1/CanCM4-rcp45-tasmax-r1i1p1.nc'
    return fp

@pytest.fixture(scope="session")
def nc_3d_360day(request):
    nc = get_base_3d_nc({'time': 360, 'lon': 2, 'lat': 2}, calendar='360_day')

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope="session")
def nc_3d_365day(request):
    nc = get_base_3d_nc({'time': 365, 'lon': 2, 'lat': 2}, calendar='365_day')

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope="session")
def nc_3d_standard(request):
    nc = get_base_3d_nc({'time': 366, 'lon': 2, 'lat': 2}, calendar='standard')

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope="session")
def nc_3d_360day_tstart_15(request):
    nc = get_base_3d_nc({'time': 360, 'lon': 2, 'lat': 2}, calendar='360_day', start_time=15)

    def teardown():
        nc.close()
    request.addfinalizer(teardown)

    return nc


@pytest.fixture(scope="session")
def dpm_365(request):
    return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

@pytest.fixture(scope="session")
def days_365(request):
    return [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

@pytest.fixture(scope="session")
def dpm_360(request):
    return [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]

@pytest.fixture(scope="session")
def days_360(request):
    return [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]

@pytest.fixture(scope="session")
def dpm_leap(request):
    return [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

@pytest.fixture(scope="session")
def days_leap(request):
    return [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
