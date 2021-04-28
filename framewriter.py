class FrameWriter(object):
    """
    Class for validating and writing individual data frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    frame_length -- size of an idividual in bytes *with* the frame 
        header/delimiter
    frame_header -- header for each frame used to split frames in earlier step
    frame_footer -- footer for each frame if present
    """
    def __init__(self, write_file, frame_header, frame_footer=None, frame_spacers=None, frame_length = 1024):
        self.frame_length = frame_length
        self.write_file = write_file
        self.write_file_object = open(write_file, "wb")
        self.current_frame = None
        self.past_frame_ids = []
        self.frame_header = frame_header
        self.frame_footer = frame_footer

        if frame_spacers != None:
            assert all(isinstance(item, tuple) for item in frame_spacers), "frame_spacers should be a list of (start location, spacer) tuples"
            assert all(len(item) == 2 for item in frame_spacers), "frame_spacers should be a list of (start location, spacer) tuples"
        self.frame_spacers = frame_spacers

    def validate(self, frame):
        """
        Method to validate is a provided frame from the camera stream is a
        valid format

        Arguments
        ---------
        frame -- a raw binary frame from the FlEye camera with header removed
        """
        if (len(frame) + len(self.frame_header)) != self.frame_length:
            return False

        if (self.frame_footer != None):
            footer_length = len(self.frame_footer)
            if frame[-footer_length:] != self.frame_footer:
                return False

