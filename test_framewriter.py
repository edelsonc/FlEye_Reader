import pytest
import tempfile
from framewriter import FrameWriter

@pytest.fixture
def test_frames():
    """
    Use binary file created by `create_test_file.py` to simulate 100 frame of
    random camera data. 
    """
    with open("Data/testy.bin", 'rb') as f:
        data = f.read()
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
    framewriter = FrameWriter(write_file.name, delimiters[0], delimiters[1])

    assert framewriter.frame_length == 1024
    assert framewriter.write_file == write_file.name
    assert framewriter.current_frame == None
    assert framewriter.past_frame_ids == []
    assert framewriter.frame_header == delimiters[0]
    assert framewriter.frame_footer == delimiters[1]

    # next we ensure that attempting to create an instance without all of the
    # keyword arguments causes a `TypeError`
    with pytest.raises(TypeError):
        framewriter = FrameWriter()

    with pytest.raises(TypeError):
        framewriter = FrameWriter(write_file.name)

    with pytest.raises(TypeError):
        framewriter = FrameWriter(frame_header = delimiters[0])
