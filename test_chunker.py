import pytest
from chunker import Chunker

def test_default_initial_arguments():
    chunker = Chunker()
    assert chunker.block_size == 512
    assert chunker.block_number == 2
    assert chunker.chunk_overlap == 512


