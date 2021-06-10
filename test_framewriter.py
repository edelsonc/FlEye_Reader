import pytest
import logging
from random import getrandbits
from framewriter import FrameWriter
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_frames():
    """
    Use binary file created by `create_test_file.py` to simulate 100 frame of
    random camera data.
    """
    data = bytes(test_data(25))
    return data.split(b'\xbf' * 12)


def test_FrameWriter_init(caplog, tmpdir):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    assert framewriter.write_file == tmpdir.join("write.bin")
    assert "FrameWriter initialized" in caplog.text 

