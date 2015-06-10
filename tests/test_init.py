from pyclimate import Cmip5File, Cmip3File, model_run_filter, get_model_set

def test_model_set():
    ms = get_model_set('pcic12')
    assert len(ms.keys()) == 12

def test_cmip5file(cmip5_file_list):
    for f in cmip5_file_list:
        cf = Cmip5File(f)
        assert cf.fullpath

def test_cmip5_to_cmip3_conversion(cmip5_file_list):
    for f in cmip5_file_list:
        cf = Cmip5File(f)
        assert cf.cmip3_fullpath

def test_cmip3file(cmip3_file_list):
    for f in cmip3_file_list:
        cf = Cmip3File(f)
        assert cf.fullpath


def test_model_set_filter(cmip5_file_list):
    ms = get_model_set('pcic12')
    print(cmip5_file_list)
    file_list = [x for x in cmip5_file_list if model_run_filter(x, ms)]
    assert len(file_list) == 10
