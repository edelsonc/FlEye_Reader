import pytest
import tempfile
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


@pytest.fixture
def write_file():
    """
    Creates a temporary write file for use with FrameWriter
    """
    t = tempfile.NamedTemporaryFile()
    return t


@pytest.fixture
def delimiters():
    """
    Header and footer for frames
    """
    return (b'\xbf' * 12, b'\xef' * 16)


def test_FrameWriter_init(write_file, delimiters):
    # first we check that it creates an instance with reasonable defaults
    framewriter = FrameWriter(write_file.name, delimiters[0])

    assert framewriter.frame_length == 1024
    assert framewriter.write_file == write_file.name
    assert framewriter.current_frame == None
    assert framewriter.past_frame_ids == []
    assert framewriter.frame_header == delimiters[0]
    assert framewriter.frame_footer == None
    assert framewriter.unpack_string == None

    framewriter2 = FrameWriter(write_file.name, delimiters[0], delimiters[1])
    assert framewriter2.frame_footer == delimiters[1]


def test_FrameWriter_incorrect_arguments(write_file, delimiters):
    # next we ensure that attempting to create an instance without all of the
    # keyword arguments causes a `TypeError`
    with pytest.raises(TypeError):
        framewriter = FrameWriter()

    with pytest.raises(TypeError):
        framewriter = FrameWriter(write_file.name)

    with pytest.raises(TypeError):
        framewriter = FrameWriter(frame_header = delimiters[0])


def test_FrameWriter_validate(write_file, delimiters, test_frames):
    framewriter = FrameWriter(write_file.name, delimiters[0], delimiters[1])

    # test a frame that is too short
    assert framewriter.validate(test_frames[0]) == False
    
    # correct length frame but not the correct structure
    assert framewriter.validate(bytes([getrandbits(8) for _ in range(1012)])) == False

    # Frame with correct structure but random check_sum
    assert framewriter.validate(test_frames[10]) == False

    # Frame with correct length and structure
    assert framewriter.validate(good_frame) == True


