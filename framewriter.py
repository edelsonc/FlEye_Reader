import logging

class FrameWriter(object):
    """
    Class for writing validated frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    log_file -- file for logging FrameWriter initialization and any issues
        writing frames
    """
    def __init__(self, write_file, log_file):
        self.write_file = write_file
        self.write_file_object = open(write_file, 'wb')

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameWriter initialized")

