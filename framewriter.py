class FrameWriter(object):
    """
    Class for validating and writing individual data frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    frame_length -- size of an idividual in bytes *with* the frame 
        header/delimiter
    """
    def __init__(self, write_file, frame_header, frame_footer=None, frame_length = 1024):
        self.frame_length = frame_length
        self.write_file = write_file
        self.write_file_object = open(write_file, "wb")
        self.current_frame = None
        self.past_frame_ids = []
        self.frame_header = frame_header
        self.frame_footer = frame_footer

    def validate(self):
        pass
