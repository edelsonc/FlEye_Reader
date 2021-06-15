import logging
import struct

class FrameWriter(object):
    """
    Class for writing validated frames from FlEye camera.

    Arguments
    ---------
    write_file -- file that parsed and validated frames are writen to
    log_file -- file for logging FrameWriter initialization and any issues
        writing frames
    """
    def __init__(self, unpack_string, write_file, log_file, block_size = 1024):
        self.unpack_string = unpack_string
        self.write_file = write_file
        self.write_file_object = open(write_file, 'wb')
        self.log_file = log_file
        self.block_size = block_size

        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("FrameWriter initialized")

    def write(self, frame):
        pass

    def _reformat_frame(self, frame):
        """
        take a frame -> break it into its 'sections' -> cast those to 4 byte
        numbers (add \x00 to each one until it's good) -> write these in write
        file -> log errors 
        """
        # break frame into each individual piece of "data"
        frame_tuple = self._unpack(frame)

        frame_number = frame[0]
        tag = frame[1]
        adc_tuple = frame[17:785]
        imu_tuple = frame[785:]

        # rearange pixels to be in ascending order
        ordered_adc = self._order_adc(frame_tuple[17:785])

        # cast everything to 4 byte numbers (32 bit)
        ordered_frame = (frame_number, tag) + ordered_adc + imu_tuple
        frame32bit = stuct.pack(">" + "I" * len(ordered_frame), *ordered_frame)

        # extend frame to block size with spacers
        n_filler = self.block_size - len(frame32bit)
        assert n_filler >= 0, "Frame {} is larger than a single block by {} bytes".format(frame_number, abs(n_filler))
        frame32bit += b"\x00" * n_filler
        return frame32bit

    def _unpack(self, frame):
        """
        Function used to take a raw validated frame and break it into its
        various components
        """
        return struct.unpack(self.unpack_string, frame)

    def _order_adc(self, adc_tuple):
        """
        Function to take raw adc data and order it by pixel id. Additionally
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

