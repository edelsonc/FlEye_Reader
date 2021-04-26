# This is a basic reader for the camera data that assumes things are properly
# formatted. This will be expanded to include validators soon
# author: Charlie
# date: 02/01/2021
import re
import struct

def process_frame(data):
    unpack_string = "I" + "B" * 16 + "x" * 16
    unpack_string += ("B" + "B" * 3) * 192 + "x" * 16
    unpack_string += "h" * 20 + "x" * (8 * 17 + 16)

    frame = struct.unpack(unpack_string, data)
    
    frame_number = frame[0]
    tag_tuple = frame[1:17]
    adc_tuple = frame[17:785]
    imu_tuple = frame[785:]
 
    tag_value = compute_tag_value(tag_tuple)
    adc_ordered = format_adc_data(adc_tuple)
    
    return frame


def compute_tag_value(tag_tuple):
    tag_avg = sum(tag_tuple) / len(tag_tuple)
    if tag_avg == 255:
        return 1
    elif tag_avg == 15:
        return 0
    else:
        return 2


def format_adc_data(adc_tuple):
    adc32 = []
    for i, b in enumerate(adc_tuple):
        if i % 4 == 0:
            pixel_id = adc_tuple[i]
            pixel_value = bytes(adc_tuple[i + 1: i + 4])
            pixel_value = int.from_bytes(pixel_value, byteorder="big")
            adc32.append((pixel_id, pixel_value))

    adc32.sort(key=lambda x: x[0])
    return [x[1] for x in adc32]

if __name__ == "__main__":
    binary_file = "Data/testy.bin"
    with open(binary_file, 'rb') as f:
        data = f.read()
    
    header = b'\xbf\xbf\xbf\xbf\xbf\xbf\xbf\xbf\xbf\xbf\xbf\xbf'
    footer = b'\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef'
    result1 = re.split(header, data)
    result2 = re.split(footer, data)
    
    process_frame(result1[1])
