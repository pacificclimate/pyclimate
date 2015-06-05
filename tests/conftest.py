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

