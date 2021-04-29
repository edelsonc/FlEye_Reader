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
    def __init__(self, header, footer, spacers, frame_length = 1024):
        self.frame_length = frame_length
        self.header = header
        self.footer = footer
        self.spacers = spacers
        self.current_frame = None
        self.past_frame_ids = []

    def validate(self, frame):
        """
        Method to validate is a provided frame from the camera stream is a
        valid format

        Arguments
        ---------
        frame -- a raw binary frame from the FlEye camera with header removed
        """
        pass
#         # check frame is correct length
#         if (len(frame) + len(self.frame_header)) != self.frame_length:
#             return False

