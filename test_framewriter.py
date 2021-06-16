import pytest
import logging
from framewriter import FrameWriter
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_frames():
    """
    Use binary file created by `create_test_file.py` to simulate 25 frame of
    random camera data.
    """
    data = bytes(test_data(25))
    return data.split(b'\xbf' * 12)


@pytest.fixture
def unpack_string():
    """
    Create an unpack string for our binary data
    """
    unpack_string = ">I" + "B" * 16 + "x" * 16
    unpack_string += ("B" + "B" * 3) * 192 + "x" * 16
    unpack_string += "H" * 20 + "x" * (8 * 17 + 16)
    return unpack_string


def test_FrameWriter_init(caplog, tmpdir, unpack_string):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    assert framewriter.write_file == tmpdir.join("write.bin")
    assert framewriter.log_file == tmpdir.join("framewriter.log")
    assert "FrameWriter initialized" in caplog.text 


def test_FrameWriter_unpack(unpack_string, tmpdir, test_frames):
    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))
    broken_frame = test_frames[1]
    assert len(framewriter._unpack(broken_frame)) == 805


def test_FrameWriter_order_adc(unpack_string, tmpdir):
    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    rand_adc = (0x01, 0x84, 0x15, 0x8a,
                0x00, 0xf2, 0xa5, 0xcf,
                0x02, 0xd8, 0xaa, 0x10)

    res = (0xf2a5cf, 0x84158a, 0xd8aa10)
    assert framewriter._order_adc(rand_adc) == res


def test_FrameWriter_reformat_frame(unpack_string, tmpdir, test_frames):
    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))
    reformatted_frame = framewriter._reformat_frame(test_frames[10])
    assert len(reformatted_frame) == 1024
    assert reformatted_frame[:4] == b'\x00\x00\x00\x09'
    assert reformatted_frame[4:8] == b'\x00\x00\x00' + test_frames[10][5:6]
    assert reformatted_frame[776:780] == b'\x00\x00' + test_frames[10][820:822]

    # check pixel value is correctly editted
    pixel_id = test_frames[10][36]
    new_location = pixel_id * 4 + 8
    assert reformatted_frame[new_location:new_location + 4] == b'\x00' + test_frames[10][37:40]


def test_FrameWriter_close(unpack_string, tmpdir, test_frames, caplog):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))
    framewriter.write(test_frames[10])
    framewriter.close()

    assert "FrameWriter write file closed" in caplog.text

    framewriter.write(test_frames[17])
    assert "ValueError: write to closed file" in caplog.text

def test_FrameWriter_write(unpack_string, tmpdir, test_frames):
    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))
    framewriter.write(test_frames[10])
    framewriter.close()

    with open(tmpdir.join("write.bin"), "rb") as f:
        reformatted_frame = framewriter._reformat_frame(test_frames[10])
        assert f.read(1024) == reformatted_frame
 
