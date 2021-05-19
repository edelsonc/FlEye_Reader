import pytest
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


def test_FrameValidator_init(delimiters):
    # first we check that it creates an instance with reasonable defaults
    spacers=[(0, 10, b'\x00')]
    framevalidator = FrameValidator(delimiters[0], delimiters[1], spacers)

    assert framevalidator.frame_length == 1024
    assert framevalidator.header == delimiters[0]
    assert framevalidator.footer == delimiters[1]
    assert framevalidator.spacers == spacers
    assert framevalidator.current_frame == None
    assert framevalidator.past_frame_ids == []


def test_FrameValidator_incorrect_arguments(delimiters):
    with pytest.raises(TypeError):
        framevalidator = FrameValidator()


def test_FrameValidator_validate(delimiters, test_frames, random_bytes):
    pass 
    # TODO test logger initialized
    # TODO test frame sequence validation
    # TODO test frame length validation
    # TODO test frame footer validation
    # TODO test spacer validation
    # TODO test checksum validation
    # TODO test tag switch validation

