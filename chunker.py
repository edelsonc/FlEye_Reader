class Chunker(object):
    """
    Class used to process raw camera stream binary data. `Chunker` breaks the
    file into individual chunks of fixed block size to avoid having all of the
    data in memory at once. Additionally, `Chunker` overlaps the chunks by a
    fixed number of blocks to ensure a camera frame isn't accidentally skipped
    in processing. It's action can be visualized as below

    [BLOCK BLOCK BLOCK BLOCK] <- Chunk 1
                      [BlOCK BLOCK BLOCK BLOCK] <- Chunk 2
                                        [BlOCK BLOCK BLOCK BLOCK] <- Chunk 3
                                            ...
    Arguments
    ---------
    data_file -- file name for the file to be read and chunked using chunker
    block_size -- size in bytes of individual blocks to be read in chunker
    block_number -- number of blocks to be read in each chunk
    chunk_overlap -- number of blocks that should overlap in each chunk
    """
    def __init__(self, data_file, block_size = 512, block_number = 10, chunk_overlap = 2):
        """
        Create instance of `Chunker` with sensible default values
        """
        self.block_size = block_size
        self.block_number = block_number
        self.chunk_overlap = chunk_overlap
        self.file = data_file
        self.file_object = open(data_file, "rb") 

    def next_chunk(self):
        """
        Read method that returns chunks. This function is responsible for both
        reading in chunks of the data file and setting the read position back
        to get overlap in chunks.

        When the end of the file is hit `next_chunk` will return the empty
        string, ''. Currently `EOFError` is not raised to allow use in the
        following way:

        data == None
        while data != "":
            do things with reading chunks

        An alternative using `EOFError` would be

        while True:
            try:
                data = chunker.next_chunk()

            except EOFError:
                break
        """
        data = self.file_object.read(self.block_size * self.block_number)
        
        if len(data) == self.block_size * self.block_number:
            self.file_object.seek(-self.block_size * self.chunk_overlap, 1)
        
        return data

