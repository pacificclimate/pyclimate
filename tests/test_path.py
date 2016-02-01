import pytest

from pyclimate import group_files_by_model_set, iter_matching_cmip5_file

@pytest.mark.parametrize(('_filter', 'expected'), [
    ([{'variable': 'tasmin'}], 5),
    ([{'variable': 'tasmax'}], 6),
    ([{'experiment': 'rcp85'}], 3)
])
def test_file_iter(cmip5_file_list, _filter, expected):
    i = iter_matching_cmip5_file(cmip5_file_list, _filter)
    assert len(list(i)) == expected

def test_model_grouping(cmip5_file_list):
    groups = group_files_by_model_set(cmip5_file_list)
    assert len(groups) == 6
    assert 'CanESM2_rcp45_r1i1p1' in groups.keys()
    assert len(groups['CanESM2_rcp45_r1i1p1']) == 2
