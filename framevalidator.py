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
    validate_checksum -- flag for if the FrameValidator instance will validate
        IMU checksums or skip this part of the process
    """
    def __init__(self, log_file, header, footer, spacers, frame_length=1024, validate_checksum=True):
        self.log_file = log_file
        self.frame_length = frame_length
        self.header = header
        self.footer = footer
        self.spacers = spacers
        self.current_frame = None
        self.past_frame_ids = {}
        self.tags = [b'\x0f' * 16, b'\xff' * 16]

        if not isinstance(validate_checksum, bool):
            raise ValueError("validate_checksum flag must be a boolean")
            
        self.validate_checksum = validate_checksum

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameValidator initialized")
        if not validate_checksum:        
            logging.debug("Checksum validation is off; IMU data is not validated")
        else:
            logging.debug("Checksum validation is on; IMU data is validated")

    def set_validate_checksum(self, validate_checksum):
        """
        Small helper method to switch checksum validation on/off
        
        Arguments
        ---------
        validate_checksum -- boolean argument to set if checksum validation occurs
        """
        if not isinstance(validate_checksum, bool):
            raise ValueError("validate_checksum flag must be a boolean")

        self.validate_checksum = validate_checksum
        logging.debug("Checksum validation is now set to:{}".format(str(validate_checksum)))

    def validate(self, frame, chunk_id, byte_loc, run_id):
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
        run_id -- ID for which recording session the camera is in
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

        # validate tag switch values
        if frame[4:20] not in self.tags:
            log_message = "Frame at {} has an invalid tag format".format(byte_loc)
            logging.warning(log_message)

        # validate checksum is correct
        start_imu = 832 - header_len
        end_imu = 872 - header_len
        imu_data = frame[start_imu:end_imu] 

        if self.validate_checksum:
            check_sum1_correct = sum(imu_data[:18])
            check_sum2_correct = sum(imu_data[20:38])

            check_sum1 = int.from_bytes(imu_data[18:20], "big")
            check_sum2 = int.from_bytes(imu_data[38:], "big")

            if check_sum1 != check_sum1_correct or check_sum2 != check_sum2_correct:
                log_message = "Frame at {} has invalid check_sum".format(byte_loc)
                logging.warning(log_message) 
                return False

        # validate frame is next in sequence 
        if run_id not in self.past_frame_ids:
            self.past_frame_ids[run_id] = []
            log_message = "Recording {} started at location {}".format(run_id, byte_loc)
            logging.debug(log_message)

        frame_id = int.from_bytes(frame[:4], "big")
        if self.past_frame_ids[run_id] == []:
            self.past_frame_ids[run_id] = [-1, frame_id]
        elif frame_id != self.past_frame_ids[run_id][1] + 1:
            log_message = "Out of order frame sequence at {}: frame {} directly after frame {} and frame {}".format(byte_loc, frame_id, self.past_frame_ids[run_id][0], self.past_frame_ids[run_id][1])
            logging.warning(log_message)
            self.past_frame_ids[run_id][0], self.past_frame_ids[run_id][1] = self.past_frame_ids[run_id][1], frame_id
        else:
            self.past_frame_ids[run_id][0], self.past_frame_ids[run_id][1] = self.past_frame_ids[run_id][1], frame_id

        return True

