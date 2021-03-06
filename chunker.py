class Chunker(object):
    """
    Class used to process raw camera stream binary data. `Chunker` breaks the
    file into individual chunks of fixed block size to avoid having all of the
    data in memory at once. Additionally, `Chunker` overlaps the chunks by a
    fixed number of blocks to ensure a camera frame isn't accidentally skipped
    in processing. It's action can be visualized as below

    [BLOCK BLOCK BLOCK BLOCK] <- Chunk 0
                      [BlOCK BLOCK BLOCK BLOCK] <- Chunk 1
                                        [BlOCK BLOCK BLOCK BLOCK] <- Chunk 2
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
        self.chunk_id = 0

    def close(self):
        """Simple method to close data file connection"""
        self.file_object.close()

    def next_chunk(self):
        """
        Read method that returns chunks. This function is responsible for both
        reading in chunks of the data file and setting the read position back
        to get overlap in chunks.

        Returns
        -------
        chunk_id -- Current chunk in the file as labeling in class docstring
        data -- the binary data in the read chunk
        byte_loc -- byte location in the read file of start of chunk
        """
        chunk_id = self.chunk_id
        byte_loc = self.file_object.tell()
        data = self.file_object.read(self.block_size * self.block_number)
        
        if len(data) == self.block_size * self.block_number:
            self.file_object.seek(-self.block_size * self.chunk_overlap, 1)
            self.chunk_id += 1
        elif len(data) < self.block_size * self.block_number:
            self.chunk_id = "END"

        return chunk_id, data, byte_loc

    def rewind(self):
        """
        Rewinds the read file to allow reading of the data again
        """
        self.file_object.seek(0, 0)
        self.chunk_id = 0

    @staticmethod
    def split(chunk, byte_loc, header, footer):
        """
        Class method for splitting chunks into frames. Takes a chunk as created
        by `Chunker` and splits on both header and footers for each frame. Only
        returns frames that have both a header and a footer. 

        Arguments
        ---------
        chunk, byte_loc -- returns of Chunker.next_chunk
        header, footer -- frame start and end delimiter
        """
        # first we find where the first frame starts
        first_header = chunk.find(header)
        if first_header == -1:
            return []

        # we remove everything before the first header and split on headers
        frame_loc = byte_loc + first_header
        split_frames = []
        for frame in chunk[first_header:].split(header):
            if frame == b'':
                continue
            
            footer_loc = frame.find(footer)
            if footer_loc != -1:
                split_frames.append((frame_loc, frame[:footer_loc]))
 
            frame_loc += len(header) + len(frame)

        return split_frames

