import pytest
import logging
import tempfile
from random import getrandbits
from framevalidator import FrameValidator
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_frames():
    """
    Use binary file created by `create_test_file.py` to simulate 25 frame of
    random camera data.
    """
    data = bytes(test_data(25))
    return [ frame.split(b'\xef' * 16)[0] for frame in data.split(b'\xbf' * 12) ]


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


def test_FrameValidator_init(delimiters, caplog, tmpdir):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing
    log_file = tmpdir.join("test_FrameValidator_init.log")

    spacers=[(0, 10, b'\x00')]
    framevalidator = FrameValidator(log_file, delimiters[0], delimiters[1], spacers)

    assert framevalidator.frame_length == 1024
    assert framevalidator.header == delimiters[0]
    assert framevalidator.footer == delimiters[1]
    assert framevalidator.spacers == spacers
    assert framevalidator.current_frame == None
    assert framevalidator.past_frame_ids == {}
    assert framevalidator.log_file == log_file
    assert "FrameValidator initialized" in caplog.text


def test_FrameValidator_incorrect_arguments(delimiters):
    with pytest.raises(TypeError):
        framevalidator = FrameValidator()


def test_FrameValidator_set_validate_checksum(delimiters, test_frames, tmpdir, caplog):
    caplog.set_level(logging.DEBUG)

    # create a FrameValidator instance
    log_file = tmpdir.join("test_validate.log")
    spacers=[(32, 16, b'\x00'), (816, 16, b'\x00'), (872, 136, b'\x00')]
    framevalidator = FrameValidator(log_file, delimiters[0], delimiters[1], spacers, validate_checksum=False)
    assert "Checksum validation is off; IMU data is not validated" in caplog.text

    # test checksum validation is off
    bad_check_sum = test_frames[9]
    bad_check_sum = bad_check_sum[:850] + b'\x00\x00' + bad_check_sum[852:]
    assert framevalidator.validate(bad_check_sum, 1, 512 + 1024 * 9, 0)

    # check logging when setting values and check for correct type
    framevalidator.set_validate_checksum(True)
    assert "Checksum validation is now set to:True" in caplog.text

    with pytest.raises(ValueError):
        framevalidator.set_validate_checksum("cat")


def test_FrameValidator_validate(delimiters, test_frames, random_bytes, tmpdir, caplog):
    caplog.set_level(logging.DEBUG)

    # create a FrameValidator instance
    log_file = tmpdir.join("test_validate.log")
    spacers=[(32, 16, b'\x00'), (816, 16, b'\x00'), (872, 136, b'\x00')]
    framevalidator = FrameValidator(log_file, delimiters[0], delimiters[1], spacers)

    # test frame length validation
    short_frame = random_bytes[:100]
    file_opener = test_frames[0]

    assert framevalidator.validate(short_frame, 0, 0, 0) == False
    assert "Frame at 0 is wrong length: 128 bytes instead of 1024 bytes" in caplog.text

    assert framevalidator.validate(file_opener, 49, 45, 0) == False
    assert "Frame at 45 is wrong length: 540 bytes instead of 1024 bytes" in caplog.text

    # test spacer validation
    spacer_bad = test_frames[7]
    spacer_bad = spacer_bad[:20] + b'\xbd' * 16 + spacer_bad[36:]
    assert framevalidator.validate(spacer_bad, 1, 512 + 1024 * 6, 0) == False
    assert "Frame at 6656 has invalid spacer at block position 32" in caplog.text

    # test checksum validation
    bad_check_sum = test_frames[9]
    bad_check_sum = bad_check_sum[:850] + b'\x00\x00' + bad_check_sum[852:]
    assert framevalidator.validate(bad_check_sum, 1, 512 + 1024 * 9, 0) == False
    assert "Frame at 9728 has invalid check_sum" in caplog.text

    # test tag switch validation
    bad_tag = test_frames[8]
    bad_tag = bad_tag[:4] + b'\x0f' * 8 + b'\xff'*8 + bad_tag[20:]
    framevalidator.validate(bad_tag, 1, 512 + 1024 * 7, 0)
    assert "Frame at 7680 has an invalid tag format" in caplog.text

    # test frame sequence validation
    framevalidator.validate(test_frames[1], 1, 512, 0)
    framevalidator.validate(test_frames[2], 1, 512 +1024, 0)
    framevalidator.validate(test_frames[5], 1, 512 + 1024 * 4, 0)
    assert "Out of order frame sequence at 4608: frame 4 directly after frame 0 and frame 1" in caplog.text

    framevalidator.validate(test_frames[1], 1, 512, 0)
    framevalidator.validate(test_frames[2], 1, 512 +1024, 0)
    framevalidator.validate(test_frames[3], 1, 512 + 1024 * 2, 0)
    framevalidator.validate(test_frames[1], 1, 512 + 1024 * 3, 1)
    assert "Recording 1 started at location 3584" in caplog.text

    # finally validate a correct frame
    assert framevalidator.validate(test_frames[6], 1, 512 + 1024 * 5, 0)

