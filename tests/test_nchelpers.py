import pyclimate.nchelpers as nch

def test_nc_copy_global_atts(nc_3d, nc_3d_bare):
    nch.nc_copy_atts(nc_3d, nc_3d_bare)
    assert 'model_id' in nc_3d_bare.ncattrs()
    assert 'source'  in nc_3d_bare.ncattrs()

def test_nc_copy_var_atts(nc_3d, nc_3d_bare):
    nch.nc_copy_atts(nc_3d, nc_3d_bare, 'tasmax', 'dummy_var')
    assert nc_3d_bare.variables['dummy_var'].standard_name == 'air_temperature'

def test_nc_get_360day_monthly_time_slices(nc_3d_360day):
    expected = [slice(i, i+30) for i in range(0, 360, 30)]
    slices = nch.get_monthly_time_slices(nc_3d_360day.variables['time'])
    assert slices  == expected
    for slice_ in slices:
        tasmax = nc_3d_360day.variables['tasmax']
        assert tasmax[slice_,:,:].shape == (30, 2, 2)

