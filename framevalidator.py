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

    def validate(self, frame, chunk_id, byte_loc):
        """
        Method to validate is a provided frame from the camera stream is a
        valid format

        Arguments
        ---------
        frame -- a raw binary frame from the FlEye camera with header removed
        """
        # TODO validate frame is correct length                                               
        frame_length = len(frame) + len(self.header)
        if frame_length != self.frame_length:
            log_message = "Frame at {} is wrong length: {} bytes instead of {} bytes".format(byte_loc, frame_length, self.frame_length)
            logging.warning(log_message)
            return False
 
        # TODO validate frame has footer                                                      
        footer_len = len(self.footer)
        if frame[-footer_len:] != self.footer:
            log_message = "Frame at {} is missing or has an incorrect footer".format(byte_loc)
            logging.warning(log_message)
            return False

        # TODO validate spacers are in correct positions                                      
        # TODO validate checksum is correct
        # TODO validate tag switch values
        # TODO validate frame is next in sequence 

        frame_id = int.from_bytes(frame[:4], "big")
        if self.past_frame_ids == []:
            self.past_frame_ids = [-1, frame_id]
        elif frame_id != self.past_frame_ids[1] + 1:
            log_message = "Out of order frame sequence: frame {} directly after frame {} and frame {}".format(frame_id, self.past_frame_ids[0], self.past_frame_ids[1])
            logging.warning(log_message)
            self.past_frame_ids[0], self.past_frame_ids[1] = self.past_frame_ids[1], frame_id
        else:
            self.past_frame_ids[0], self.past_frame_ids[1] = self.past_frame_ids[1], frame_id

        return True

