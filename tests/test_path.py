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
