import pyclimate.nchelpers as nch

def test_nc_copy_global_atts(nc_3d, nc_3d_bare):
    nch.nc_copy_atts(nc_3d, nc_3d_bare)
    assert 'model_id' in nc_3d_bare.ncattrs()
    assert 'source'  in nc_3d_bare.ncattrs()

def test_nc_copy_var_atts(nc_3d, nc_3d_bare):
    nch.nc_copy_atts(nc_3d, nc_3d_bare, 'tasmax', 'dummy_var')
    assert nc_3d_bare.variables['dummy_var'].standard_name == 'air_temperature'
