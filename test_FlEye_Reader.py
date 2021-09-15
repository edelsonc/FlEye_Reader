import pytest
import FlEye_Reader
from create_test_file import create_random_data_file as test_data
from chunker import Chunker

@pytest.fixture
def test_runs():
    data = b''
    for _ in range(3):
        data += bytes(test_data(5))
    return data


@pytest.fixture
def configs():
    return {"run_start": b'\xbb', "run_end": b'\xeb'}


@pytest.fixture
def camera_configs():
    config = {"run_start": b'\xbb' * 512, 
            "run_end": b'\xeb' * 512, 
            "header": b'\xbf' * 12,
            "footer": b'\xef' * 16}
    return config


def create_test_chunker(tmp_file, data):
    with open(tmp_file, "wb") as t:
        t.write(data)

    return Chunker(tmp_file)


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


def test_FlEye_Reader_find_runs(test_runs, camera_configs, tmpdir):
    read_tmpfile = tmpdir.join("test_find_runs.bin")
    chunker = create_test_chunker(read_tmpfile, test_runs)

    session = [((512 + 1024 * 5 + 512) * i, (512 + 1024 * 5) * (i + 1) + 512 * i) for i in range(3)] 
    assert FlEye_Reader.find_runs(chunker, camera_configs) == session

    chunker = create_test_chunker(read_tmpfile, test_runs + b'\x00' + test_runs)
    assert FlEye_Reader.find_runs(chunker, camera_configs) == session

    chunker = create_test_chunker(read_tmpfile, test_runs[:12288] + b'\xff' + test_runs[12288:])
    assert FlEye_Reader.find_runs(chunker, camera_configs) == session[:-1]

    chunker = create_test_chunker(read_tmpfile, b'\x0f' + test_runs)
    assert FlEye_Reader.find_runs(chunker, camera_configs) == []


def test_FlEye_Reader_get_run_id():
    sessions = [(0, 100), (101, 200), (201, 222)]
    assert FlEye_Reader.get_run_id(sessions, 10) == 0
    assert FlEye_Reader.get_run_id(sessions, 210) == 2
    assert FlEye_Reader.get_run_id(sessions, -10) == -1
    assert FlEye_Reader.get_run_id(sessions, 251) == 0xAF
    assert FlEye_Reader.get_run_id(sessions, 200) == 1

