"""My default pytest will assume that all files prefixed with
'test' are test files. This file is here to make sure that 
pytest only runs on the files it should run on.
"""

def test_1():
    assert 1 == 2