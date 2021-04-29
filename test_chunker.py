import pytest
import tempfile
from random import getrandbits
from chunker import Chunker

@pytest.fixture
def read_tmpfile():
    """Create a temporary file with random bytes"""
    t = tempfile.NamedTemporaryFile()
    t.write(bytes([getrandbits(8) for _ in range(1024 * 50)]))
    t.seek(0)
    return t       


@pytest.fixture
def small_tmpfile():
    """Creates a small temporary file with random bytes"""
    t = tempfile.NamedTemporaryFile()
    t.write(bytes([getrandbits(8) for _ in range(1024 * 5)]))
    t.seek(0)
    return t
 

def test_initialization(read_tmpfile):
    chunker = Chunker(read_tmpfile.name)
    assert chunker.file == read_tmpfile.name
    assert chunker.block_size == 512
    assert chunker.block_number == 10
    assert chunker.chunk_overlap == 2
    assert chunker.chunk_id == 0


def test_Chunker_incorrect_arguments():
    with pytest.raises(TypeError):
        chunker = Chunker()

    with pytest.raises(FileNotFoundError):
        chunker = Chunker("~/cats_the_musical.bin")


def test_basic_read(read_tmpfile):
    # read in content of temp file to check results
    tmpfile_content = read_tmpfile.read()
    read_tmpfile.seek(0)

    # create chunker and read first chunk
    chunker = Chunker(read_tmpfile.name)
    chunk_id, data, byte_loc = chunker.next_chunk()
    assert chunk_id == 0
    assert byte_loc == 0
    assert len(data) == chunker.block_size * chunker.block_number
    assert data == tmpfile_content[0:(512*10)]

    # read another chunk and check it too
    chunk_id2, data2, byte_loc = chunker.next_chunk()
    assert chunk_id2 == 1
    assert byte_loc == 512*8
    assert data2 == tmpfile_content[512*8:512*18]


def test_end_of_file(small_tmpfile):
    tmpfile_content = small_tmpfile.read()
    small_tmpfile.seek(0)

    chunker = Chunker(small_tmpfile.name)
    chunk_id1, data1, byte_loc1 = chunker.next_chunk()
    chunk_id2, data2, byte_loc2 = chunker.next_chunk()
    chunk_id3, data3, byte_loc3 = chunker.next_chunk()
    chunk_id4, data4, byte_loc4 = chunker.next_chunk()

    assert data1 == tmpfile_content
    assert data2 == tmpfile_content[-1024:]
    assert data3 == b""
    assert data4 == b""

    assert chunk_id1 == 0
    assert chunk_id2 == 1
    assert chunk_id3 == "END"
    assert chunk_id4 == "END"

    assert byte_loc1 == 0
    assert byte_loc2 == 512*8
    assert byte_loc3 == len(tmpfile_content)
    assert byte_loc4 == len(tmpfile_content)


def test_close_file(read_tmpfile):
    # create a `Chunker` object and read some random data
    chunker = Chunker(read_tmpfile.name)
    chunk_id, data, byte_loc = chunker.next_chunk()

    # now we close the file and check that a new read raises an error
    chunker.close()
    with pytest.raises(ValueError):
        chunk_id, data = chunker.next_chunk()

