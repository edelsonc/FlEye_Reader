import pytest
import logging
import tempfile
from random import getrandbits
from framevalidator import FrameValidator
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_frames():
    """
    Use binary file created by `create_test_file.py` to simulate 100 frame of
    random camera data.
    """
    data = bytes(test_data(25))
    return data.split(b'\xbf' * 12)


@pytest.fixture
def log_file():
    """
    Create a temporary named file for logging
    """
    return tempfile.NamedTemporaryFile()


@pytest.fixture
def write_file():
    """
    Create a temporary named file for writing frames
    """
    return tempfile.NamedTemporaryFile()


def test_FrameWriter_init(delimiters, log_file, write_file, caplog):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

