import logging
import struct

class FrameWriter(object):
    """
    Class for writing validated frames from FlEye camera.

    Arguments
    ---------
    unpack_string -- string used to unpack the raw byte data into numerical
        types; as specified at https://docs.python.org/3/library/struct.html#format-strings
    write_file -- file that parsed and validated frames are writen to
    log_file -- file for logging FrameWriter initialization and any issues
        writing frames
    block_size -- size of data blocks you will write. FrameWriter will pad
        reformatted data to have this many bytes.
    """
    def __init__(self, unpack_string, write_file, log_file, block_size = 1024):
        self.unpack_string = unpack_string
        self.write_file = write_file
        self.write_file_object = open(write_file, 'wb')
        self.log_file = log_file
        self.block_size = block_size

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameWriter initialized")

    def write(self, frame, run_id):
        """
        Public facing fuction used to reformatted and write a frame to the
        FrameWriter.write_file

        Arguments
        ---------
        frame -- fly camera frame validated by FrameValidator
        """
        try:
            run_idu32 = run_id.to_bytes(4, "big")
            reformatted_frame = self._reformat_frame(frame)
            self.write_file_object.write(run_idu32 + reformatted_frame)
        except Exception as Argument:
            frame_id = int.from_bytes(frame[:4], "big")
            logging.exception("Error occured while writing Frame {}".format(frame_id))

    def close(self):
        """
        Public facing function to close the write file after processing a data
        file is complete
        """
        self.write_file_object.close()
        logging.debug("FrameWriter write file closed")

    def _reformat_frame(self, frame):
        """
        Function to parse a data frame, organize the pixels by id, and 
        reformatted/pad all numbers to be 4 bytes

        NOTE: IMU data should be treated as 16 bit unsigned integers. For these
        values the writing to 4 bytes should be thought of as adding two
        padding bytes of the format 0x00.

        Arguments
        ---------
        frame -- fly camera frame validated by FrameValidator
        """
        # break frame into each individual piece of "data"
        frame_tuple = self._unpack(frame)

        frame_number = frame_tuple[0]
        tag = frame_tuple[1]
        adc_tuple = frame_tuple[17:785]
        imu_tuple = frame_tuple[785:]

        # rearange pixels to be in ascending order
        ordered_adc = self._order_adc(frame_tuple[17:785])

        # cast everything to 4 byte numbers (32 bit)
        ordered_frame = (frame_number, tag) + ordered_adc + imu_tuple
        frame32bit = struct.pack(">" + "I" * len(ordered_frame), *ordered_frame)

        # extend frame to block size with spacers
        n_filler = self.block_size - len(frame32bit) - 4  # -4 for run ID
        assert n_filler >= 0, "Frame {} is larger than a single block by {} bytes".format(frame_number, abs(n_filler))
        frame32bit += b"\x00" * n_filler

        return frame32bit

    def _unpack(self, frame):
        """
        Private function used to take a raw validated frame and break it into its
        various components
        """
        return struct.unpack(self.unpack_string, frame)

    def _order_adc(self, adc_tuple):
        """
        Private function to take raw adc data and order it by pixel id. Additionally
        casts to 32 bit
        """
        adc32 = []
        for i, b in enumerate(adc_tuple):
            if i % 4 == 0:
                pixel_id = adc_tuple[i]
                pixel_value = bytes(adc_tuple[i + 1: i + 4])
                pixel_value = int.from_bytes(pixel_value, byteorder="big")
                adc32.append((pixel_id, pixel_value))

        adc32.sort(key=lambda x: x[0])
        return tuple((x[1] for x in adc32))

