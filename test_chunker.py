import pytest
from chunker import Chunker
from test_helpers import random_bytes, small_random_bytes

def test_initialization(tmpdir):
    read_tmpfile = tmpdir.join("test_init.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    chunker = Chunker(read_tmpfile)
    assert chunker.file == read_tmpfile
    assert chunker.block_size == 1024
    assert chunker.block_number == 10
    assert chunker.chunk_overlap == 1
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


def test_Chunker_split(tmpdir):
    read_tmpfile = tmpdir.join("test_split.bin")
    tmpfile_content = random_bytes(read_tmpfile)

    test_chunk = b"\x00\x00\x00\x00\xff\xff\x00\x00\x00\xff\xff\x00"
    chunker = Chunker(read_tmpfile)
    split_chunks = Chunker.split(test_chunk, 0, b"\xff\xff")

    assert len(split_chunks) == 3
    assert split_chunks[1] == (6, b'\x00\x00\x00')

