class FrameWriter(object):
    """
    Class for validating and writing individual data frames from FlEye camera.
    """
    def __init__(self, write_file, frame_length = 1012):
        self.frame_length = frame_length
        self.write_file = write_file
        self.write_file_object = open(write_file, "wb")

