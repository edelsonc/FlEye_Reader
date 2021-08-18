import pytest
from random import getrandbits
from chunker import Chunker
from create_test_file import create_random_data_file as test_data

@pytest.fixture
def test_runs():
    data = bytes(test_data(5))
    return data


def random_bytes(tmp_file):
    """Create a temporary file with random bytes"""
    with open(tmp_file, "wb") as t:
        data = bytes([getrandbits(8) for _ in range(1024 * 50)])
        t.write(data)       
    return data


def small_random_bytes(tmp_file):
    """Creates a small temporary file with random bytes"""
    with open(tmp_file, "wb") as t:
        data = bytes([getrandbits(8) for _ in range(1024 * 5)])
        t.write(data)
    return data


# def create_test_file(tmp_file, data)
#     with open(tmp_file, "wb") as t:
#         t.write(data)


def test_initialization(tmpdir):
    read_tmpfile = tmpdir.join("test_init.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    chunker = Chunker(read_tmpfile)
    assert chunker.file == read_tmpfile
    assert chunker.block_size == 512
    assert chunker.block_number == 10
    assert chunker.chunk_overlap == 2
    assert chunker.chunk_id == 0


def test_Chunker_incorrect_arguments():
    with pytest.raises(TypeError):
        chunker = Chunker()

    with pytest.raises(FileNotFoundError):
        chunker = Chunker("~/cats_the_musical.bin")


def test_basic_read(tmpdir):
    read_tmpfile = tmpdir.join("test.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    # create chunker and read first chunk
    chunker = Chunker(read_tmpfile)
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


def test_end_of_file(tmpdir):
    small_tmpfile = tmpdir.join("test_OEF.bin")
    tmpfile_content = small_random_bytes(small_tmpfile)

    chunker = Chunker(small_tmpfile)
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


def test_close_file(tmpdir):
    # create a `Chunker` object and read some random data
    read_tmpfile = tmpdir.join("test_close.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    chunker = Chunker(read_tmpfile)
    chunk_id, data, byte_loc = chunker.next_chunk()

    # now we close the file and check that a new read raises an error
    chunker.close()
    with pytest.raises(ValueError):
        chunk_id, data = chunker.next_chunk()


def test_Chunker_split(test_runs):
    test_chunk = b"\x00\x00\xef\x00"
    split_chunks = Chunker.split(test_chunk, 0, b"\xff\xff", b"\xef")
    assert split_chunks == [] 
    
    test_chunk = b"\x00\x00\x00\x00\xff\xff\x00\x00\x00\xff\xff\x00"
    split_chunks = Chunker.split(test_chunk, 0, b"\xff\xff", b'\xef')
    assert split_chunks == []

    test_chunk = b"\xaa\xff\xff\x00\x00\x00\x00\xef\xff\xff\x00\x00\x00\xef\xff\xff\x00\xef"
    split_chunks = Chunker.split(test_chunk, 0, b"\xff\xff", b'\xef')
    assert split_chunks == [(1, b'\x00\x00\x00\x00'), (8, b'\x00\x00\x00'), (14, b'\x00')]

    # test split on simulated data
    split_chunks = Chunker.split(test_runs, 0, b'\xbf'*12, b'\xef'*16)
    assert len(split_chunks) == 5
    assert split_chunks[0] == (512, test_runs[524:1520])


def test_Chunker_rewind(tmpdir):
    read_tmpfile = tmpdir.join("test_rewind.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    chunker = Chunker(read_tmpfile)
    _, first_chunk, _ = chunker.next_chunk()
    while chunker.chunk_id != "END":
        _, _, _ = chunker.next_chunk()

    chunker.rewind()
    assert chunker.chunk_id == 0

    _, test_chunk, _ = chunker.next_chunk()
    assert test_chunk == first_chunk 

