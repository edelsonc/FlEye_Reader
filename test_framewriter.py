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

def test_FrameWriter_init(write_file):
    framewriter = FrameWriter(write_file.name)

    assert framewriter.frame_length == 1012
    assert framewriter.write_file == write_file.name

    with pytest.raises(TypeError):
        framewriter = FrameWriter()
