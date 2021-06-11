import pytest
import logging
from random import getrandbits
from framewriter import FrameWriter
from create_test_file import create_random_data_file as test_data

def test_FrameWriter_init(caplog, tmpdir):
    caplog.set_level(logging.DEBUG)  # set logger capture to debug for testing

    framewriter = FrameWriter(tmpdir.join("write.bin"), tmpdir.join("framewriter.log"))

    assert framewriter.write_file == tmpdir.join("write.bin")
    assert "FrameWriter initialized" in caplog.text 

