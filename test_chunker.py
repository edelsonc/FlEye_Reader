import pytest
import tempfile
from random import getrandbits
from chunker import Chunker

@pytest.fixture
def read_tempfile():
    """Create a temporary file with random bytes"""
    t = tempfile.NamedTemporaryFile(delete=False)
    t.write(bytes([getrandbits(8) for _ in range(1024 * 50)]))
    return t       

def test_initialization(read_tempfile):
    chunker = Chunker(read_tempfile.name)
    assert chunker.file == read_tempfile.name
    assert chuner.file_object == read_tempfile
    assert chunker.block_size == 512
    assert chunker.block_number == 10
    assert chunker.chunk_overlap == 512

    with pytest.raises(TypeError):
        chunker = Chunker()

    with pytest.raises(FileNotFoundError):
        chunker = Chunker("~/cats_the_musical.bin")


