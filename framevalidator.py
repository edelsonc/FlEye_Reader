import logging

class FrameValidator(object):
    """
    Class for validating and writing individual data frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    frame_length -- size of an idividual in bytes *with* the frame 
        header/delimiter
    frame_header -- header for each frame used to split frames in earlier step
    frame_footer -- footer for each frame if present
    unpack_string -- string used to decode byte data into associated types
    """
    def __init__(self, log_file, header, footer, spacers, frame_length = 1024):
        self.log_file = log_file
        self.frame_length = frame_length
        self.header = header
        self.footer = footer
        self.spacers = spacers
        self.current_frame = None
        self.past_frame_ids = []

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameValidator initialized")

    def validate(self, frame):
        """
        Method to validate is a provided frame from the camera stream is a
        valid format

        Arguments
        ---------
        frame -- a raw binary frame from the FlEye camera with header removed
        """
        pass
        # TODO validate frame is next in sequence                                             
        
        # TODO validate frame is correct length                                               
        # TODO validate frame has footer                                                      
        # TODO validate spacers are in correct positions                                      
        # TODO validate checksum is correct
        # TODO validate tag switch values

        # # check frame is correct length
        # if (len(frame) + len(self.frame_header)) != self.frame_length:
        #     return False

