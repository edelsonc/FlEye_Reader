import pytest
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
def write_file():
    """
    Creates a temporary write file for use with FrameValidator
    """
    t = tempfile.NamedTemporaryFile()
    return t


@pytest.fixture
def delimiters():
    """
    Header and footer for frames
    """
    return (b'\xbf' * 12, b'\xef' * 16)


def test_FrameValidator_init(write_file, delimiters):
    # first we check that it creates an instance with reasonable defaults
    framevalidator = FrameValidator(write_file.name, delimiters[0])

    assert framevalidator.frame_length == 1024
    assert framevalidator.write_file == write_file.name
    assert framevalidator.current_frame == None
    assert framevalidator.past_frame_ids == []
    assert framevalidator.frame_header == delimiters[0]
    assert framevalidator.frame_footer == None
    assert framevalidator.unpack_string == None

    framevalidator2 = FrameValidator(write_file.name, delimiters[0], delimiters[1])
    assert framevalidator2.frame_footer == delimiters[1]


def test_FrameValidator_incorrect_arguments(write_file, delimiters):
    # next we ensure that attempting to create an instance without all of the
    # keyword arguments causes a `TypeError`
    with pytest.raises(TypeError):
        framevalidator = FrameValidator()

    with pytest.raises(TypeError):
        framevalidator = FrameValidator(write_file.name)

    with pytest.raises(TypeError):
        framevalidator = FrameValidator(frame_header = delimiters[0])


def test_FrameValidator_validate(write_file, delimiters, test_frames):
    framevalidator = FrameValidator(write_file.name, delimiters[0], delimiters[1])

    # test a frame that is too short
    assert framevalidator.validate(test_frames[0]) == False
    
    # correct length frame but not the correct structure
    assert framevalidator.validate(bytes([getrandbits(8) for _ in range(1012)])) == False

    # Frame with correct structure but random check_sum
    assert framevalidator.validate(test_frames[10]) == False

    # Frame with correct length and structure
    assert framevalidator.validate(good_frame) == True


