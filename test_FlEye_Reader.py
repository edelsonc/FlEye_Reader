import pytest
import FlEye_Reader
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_runs():
    data = b''
    for _ in range(5):
        data += bytes(test_data(5))
    return data


def test_FlEye_Reader_intersections():
    x = [(1, 15), (17, 22)]
    assert not FlEye_Reader.intersections(x) 

    x = [(1, 15), (3, 15)]
    assert FlEye_Reader.intersections(x)

    x = [(2, 16), (4, 18)]
    assert FlEye_Reader.intersections(x)


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

