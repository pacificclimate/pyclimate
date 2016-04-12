import pytest

from pyclimate.path import group_files_by_model_set, iter_matching_cmip5_file

@pytest.mark.parametrize(('_filter', 'expected'), [
    ("[{'variable_name': 'tasmin'}]", 5),
    ("[{'variable_name': 'tasmax'}]", 6),
    ("[{'experiment': 'rcp85'}]", 3)
])
def test_file_iter(cmip5_file_list, _filter, expected):
    i = iter_matching_cmip5_file(cmip5_file_list, _filter)
    assert len(list(i)) == expected

def test_pcic12_filter(cmip5_file_list):
    fl = '''/root/directory/CCCMA/CanESM2/rcp85/day/atmos/day/r1i1p1/v20120407/tasmin/tasmin_day_CanESM2_rcp85_r1i1p1_20060101-21001231.nc
/root/directory/CCCMA/CanESM2/rcp60/day/atmos/day/r1i1p1/v20120407/pr/pr_day_CanESM2_rcp60_r1i1p1_20060101-21001231.nc
/root/directory/CCCMA/CanCM4/historical/day/atmos/day/r1i1p1/v20120612/pr/pr_day_CanCM4_historical_r1i1p1_19610101-20051231.nc
/root/directory/CCCMA/CanESM2/rcp26/day/atmos/day/r1i1p1/v20120407/tasmin/tasmin_day_CanESM2_rcp26_r1i1p1_20060101-21001231.nc'''.split('\n')

    i = list(iter_matching_cmip5_file(fl, 'pcic12'))
    print(i)
    assert fl[0] in i
    assert fl[1] not in i
    assert fl[2] not in i
    assert fl[3] in i

def test_model_grouping(cmip5_file_list):
    groups = group_files_by_model_set(cmip5_file_list)
    assert len(groups) == 6
    assert 'CanESM2_rcp45_r1i1p1_20060101-23001231' in groups.keys()
    assert len(groups['CanESM2_rcp45_r1i1p1_20060101-23001231'].variables) == 2
