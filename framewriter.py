import logging
import struct

class FrameWriter(object):
    """
    Class for writing validated frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    log_file -- file for logging FrameWriter initialization and any issues
        writing frames
    """
    def __init__(self, unpack_string, write_file, log_file):
        self.unpack_string = unpack_string
        self.write_file = write_file
        self.write_file_object = open(write_file, 'wb')
        self.log_file = log_file

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameWriter initialized")

    def write(self, frame):
        """
        take a frame -> break it into its 'sections' -> cast those to 4 byte
        numbers (add \x00 to each one until it's good) -> write these in write
        file -> log errors 
        """
        # TODO break frame into each individual piece of "data"
        # TODO rearange pixels to be in ascending order
        # TODO cast everything to 4 byte numbers (32 bit)
        # TODO log error (wrap in try except?)
        pass

    def _unpack(self, frame):
        """
        Function used to take a raw validated frame and break it into its
        various components
        """
        return struct.unpack(self.unpack_string, frame)
