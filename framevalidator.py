import logging

class FrameValidator(object):
    """
    Class for validating and writing individual data frames from FlEye camera.

    Arguments
    ---------
    log_file -- file that logs FrameValidator start-up and validation issues
    header -- header for each frame used to split frames in earlier step
    footer -- footer for each frame if present
    spacers -- a list of tuples for spacer locations; has format (spacer start
        location, spacer length, spacer byte) where lengths and location are in
        bytes
    frame_length -- size of an idividual in bytes *with* the frame 
        header/delimiter
    """
    def __init__(self, log_file, header, footer, spacers, frame_length = 1024):
        self.log_file = log_file
        self.frame_length = frame_length
        self.header = header
        self.footer = footer
        self.spacers = spacers
        self.current_frame = None
        self.past_frame_ids = []
        self.tags = [b'\x0f' * 16, b'\xff' * 16]

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameValidator initialized")

    def validate(self, frame, chunk_id, byte_loc):
        """
        Method to validate is a provided frame from the camera stream is a
        valid format

        Arguments
        ---------
        frame -- a raw binary frame from the FlEye camera with header removed
        chunk_id -- the id of the chunk; one of the returns of 
            Chunker.next_chunk
        byte_loc -- the byte location of the beginning of the frame in the
            raw data file
        """
        # validate frame is correct length                                               
        header_len = len(self.header)
        footer_len = len(self.footer)
        frame_length = len(frame) + header_len + footer_len
        if frame_length != self.frame_length:
            log_message = "Frame at {} is wrong length: {} bytes instead of {} bytes".format(byte_loc, frame_length, self.frame_length)
            logging.warning(log_message)
            return False

        # validate spacers are in correct positions                                      
        for spacer in self.spacers:
            begin = spacer[0] - header_len
            end = begin + spacer[1]
            if spacer[2] * spacer[1] != frame[begin:end]:
                log_message = "Frame at {} has invalid spacer at block position {}".format(byte_loc, spacer[0])
                logging.warning(log_message)
                return False

        # TODO validate checksum is correct
        # validate tag switch values
        if frame[4:20] not in self.tags:
            log_message = "Frame at {} has an invalid tag format".format(byte_loc)
            logging.warning(log_message)

        # validate frame is next in sequence 
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

