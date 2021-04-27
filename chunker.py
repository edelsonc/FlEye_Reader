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
    block_size -- size of individual blocks to be read in chunker
    block_number -- number of blocks to be read in each chunk
    chunk_overlap -- number of blocks that should overlap in each chunk
    """
    def __init__(self, data_file, block_size = 512, block_number = 10, chunk_overlap = 1):
        """create instance of `Chunker` with sensible default values"""
        self.block_size = block_size
        self.block_number = block_number
        self.chunk_overlap = chunk_overlap
        self.file = data_file
        self.file_object = open(data_file, "rb") 
