from pyclimate import Cmip5File, Cmip3File

def test_cmip5file_repr(cmip5_file):
    cf = Cmip5File(cmip5_file)
    repr(cf)
    assert eval(repr(cf)) == cf

def test_cmip5file(cmip5_file_list):
    for f in cmip5_file_list:
        cf = Cmip5File(f)
        assert cf.fullpath

def test_cmip5_to_cmip3_conversion(cmip5_file_list):
    for f in cmip5_file_list:
        cf = Cmip5File(f)
        assert cf.cmip3_fullpath

def test_cmip3file_repr(cmip3_file):
    cf = Cmip3File(cmip3_file)
    assert eval(repr(cf)) == cf

def test_cmip3file(cmip3_file_list):
    for f in cmip3_file_list:
        cf = Cmip3File(f)
        assert cf.fullpath
