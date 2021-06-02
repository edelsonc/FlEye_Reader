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
def delimiters():
    """
    Header and footer for frames
    """
    return (b'\xbf' * 12, b'\xef' * 16)


@pytest.fixture
def random_bytes():
    """
    Create a single frame of random bytes
    """
    data = bytes([getrandbits(8) for _ in range(1024)])    
    return data


@pytest.fixture
def log_file():
    """
    Create a temporary named file for logging
    """
    return tempfile.NamedTemporaryFile()


def test_FrameValidator_init(delimiters, log_file, caplog):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    spacers=[(0, 10, b'\x00')]
    framevalidator = FrameValidator(log_file.name, delimiters[0], delimiters[1], spacers)

    assert framevalidator.frame_length == 1024
    assert framevalidator.header == delimiters[0]
    assert framevalidator.footer == delimiters[1]
    assert framevalidator.spacers == spacers
    assert framevalidator.current_frame == None
    assert framevalidator.past_frame_ids == []
    assert framevalidator.log_file == log_file.name
    assert "FrameValidator initialized" in caplog.text

def test_FrameValidator_incorrect_arguments(delimiters):
    with pytest.raises(TypeError):
        framevalidator = FrameValidator()


def test_FrameValidator_validate(delimiters, test_frames, random_bytes, log_file, caplog):
    # TODO test frame length validation
    short_frame = random_bytes[:100]
    file_opener = test_frames[0]

    spacers=[(0, 10, b'\x00')]
    framevalidator = FrameValidator(log_file.name, delimiters[0], delimiters[1], spacers)
    assert framevalidator.validate(short_frame, 0, 0) == False
    assert "Frame at 0 is wrong length: 112 bytes instead of 1024 bytes" in caplog.text

    assert framevalidator.validate(file_opener, 49, 45) == False
    assert "Frame at 45 is wrong length: 524 bytes instead of 1024 bytes" in caplog.text

    # TODO test frame sequence validation
    framevalidator.validate(test_frames[1], 1, 512)
    framevalidator.validate(test_frames[2], 1, 512 +1024)
    assert framevalidator.validate(test_frames[5], 1, 512 + 1024 * 4) == False
    assert "Out of order frame sequence: frame 4 directly after frame 0 and frame 1" in caplog.text
    # TODO test frame footer validation
    # TODO test spacer validation
    # TODO test checksum validation
    # TODO test tag switch validation

