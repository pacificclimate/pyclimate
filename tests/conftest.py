import os
import pytest

from tempfile import NamedTemporaryFile

import netCDF4
import numpy as np

@pytest.fixture(scope="session")
def nc_3d(request):
    f = NamedTemporaryFile(suffix='.nc')
    dims = {'time': 32, 'lon': 128, 'lat': 64}
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
    var_time[:] = range(dims['time'])

    var_time.axis = 'T'
    var_time.unit = 'days since 1850-1-1'
    var_time.calendar = '365_day'
    var_time.long_name = 'time'

    var = nc.createVariable('tasmax', 'f4', ('time', 'lat', 'lon'), fill_value=1e20)
    var.standard_name = "air_temperature"
    var.long_name = "Daily Maximum Near-Surface Air Temperature"
    var.units = 'K'
    var.missing_value = 1e20
    for t in range(dims['time']):
        var[t,:,:] = np.random.randn(dims['lat'], dims['lon'])

    def teardown():
        nc.close()
        f.close()
    request.addfinalizer(teardown)

    return nc

@pytest.fixture(scope="session")
def nc_3d_bare(request):
    f = NamedTemporaryFile()
    dims = {'time': 32, 'lon': 128, 'lat': 64}
    nc = netCDF4.Dataset(f.name, 'w')
    lat = nc.createDimension('lat', dims['lat'])
    lon = nc.createDimension('lon', dims['lon'])
    time = nc.createDimension('time', dims['time'])
    some_var = nc.createVariable('dummy_var','f4',('time', 'lat', 'lon'))

    def teardown():
        nc.close()
        os.remove(f.name)
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
