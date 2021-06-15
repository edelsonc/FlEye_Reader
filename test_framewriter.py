import pytest
import logging
from random import getrandbits
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
    unpack_string = "I" + "B" * 16 + "x" * 16
    unpack_string += ("B" + "B" * 3) * 192 + "x" * 16
    unpack_string += "h" * 20 + "x" * (8 * 17 + 16)
    return unpack_string


def test_FrameWriter_init(caplog, tmpdir, unpack_string):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    assert framewriter.write_file == tmpdir.join("write.bin")
    assert framewriter.log_file == tmpdir.join("framewriter.log")
    assert "FrameWriter initialized" in caplog.text 


def test_FrameWriter_write(caplog, tmpdir, test_frames, unpack_string):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(unpack_string, tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    # TODO test break frame into each individual piece of "data"
    broken_frame = test_frames[1]
    assert len(framewriter._unpack(broken_frame)) == 805

    # TODO test rearange pixels to be in ascending order
    rand_adc = (0x01, 0x84, 0x15, 0x8a,
                0x00, 0xf2, 0xa5, 0xcf,
                0x02, 0xd8, 0xaa, 0x10)

    res = (0xf2a5cf, 0x84158a, 0xd8aa10)

    assert framewriter._order_adc(rand_adc) == res

    # TODO test cast everything to 4 byte numbers (32 bit)
    # TODO test log error (wrap in try except?)

