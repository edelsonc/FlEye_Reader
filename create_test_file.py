# make a binary file with a series of random frames for practicing parsing the
# camera data
# author: Charlie Edelson
# date: 01/26/2021
import numpy as np

def create_random_frame(frame_number):
    header = [0xbf] * 12
    
    # convert frame_number to its 24 byte hex representation
    frame_number_binary = '{0:032b}'.format(frame_number)
    frame_number_bytes = [int(frame_number_binary[i:i+8], 2) for i in range(0, 32, 8)]

    # create a tag switch line
    tag_state = np.random.randint(0,2)
    tag_switch = ((1 - tag_state) * [0x0f] + tag_state * [0xff]) * 16
    
    spacer = [0x00] * 16
    
    # create random readings for the photodiode values
    pixel_order = np.random.choice(np.arange(0,192), 192, False)
    adc_values = []
    for p in pixel_order:
        adc_values.append(p)
        adc_values += np.random.randint(0, 256, 3).tolist()

    imu_data = np.random.randint(0,256, 40).tolist()
    padding = [0x00] * 8 * 17
    footer = [0xef] * 16

    frame = header + frame_number_bytes + tag_switch + spacer + adc_values + spacer + imu_data + padding + footer
    return frame


if __name__ == "__main__":
    with open("Data/testy.bin", "wb") as f:
        test_file = [0xbb] * 512
        for i in range(100):
            test_file += create_random_frame(i)
        test_file += [0xeb] * 512
    
        f.write(bytearray(test_file))

