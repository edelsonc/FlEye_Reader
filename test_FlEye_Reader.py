import pytest
import FlEye_Reader
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_runs():
    data = b''
    for _ in range(5):
        data += bytes(test_data(5))
    return data


@pytest.fixture
def configs():
    return {"run_start": b'\xbb', "run_end": b'\xeb'}


def test_FlEye_Reader_match_ranges():
    x = [0, 10, 14]
    y = [3, 13, 22]
    assert FlEye_Reader.match_ranges(x, y) == [(0, 3), (10, 13), (14, 22)]

    x = [0, 10]
    y = [3, 33, 55]
    assert FlEye_Reader.match_ranges(x, y) == [(0, 3), (10, 33)]

    x = [11, 13, 22]
    y = [15, 35, 55]
    assert FlEye_Reader.match_ranges(x, y) == [(11, 15), (13, 15), (22, 35)] 

    x = [22, 55, 103]
    y = [10, 21]
    assert FlEye_Reader.match_ranges(x, y) == []

    y = [10, 100]
    assert FlEye_Reader.match_ranges(x, y) == [(22, 100), (55, 100)]


def test_FlEye_Reader_valid_session(configs):
    runs = [(0, 22), (23, 100)]
    assert FlEye_Reader.valid_session(runs, configs) == runs

    runs = [(10, 22), (23, 100)]
    assert FlEye_Reader.valid_session(runs, configs) == []

    runs = [(0, 22), (26, 100)]
    assert FlEye_Reader.valid_session(runs, configs) == [(0, 22)]

    runs = [(0, 22), (23, 100), (109, 120), (121, 155)]
    assert FlEye_Reader.valid_session(runs, configs) == [(0, 22), (23, 100)]

    runs = []
    assert FlEye_Reader.valid_session(runs, configs) == []

