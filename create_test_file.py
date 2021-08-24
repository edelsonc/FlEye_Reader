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

    imu_data = imu_data_gen()
    padding = [0x00] * 8 * 17
    footer = [0xef] * 16

    frame = header + frame_number_bytes + tag_switch + spacer + adc_values + spacer + imu_data + padding + footer
    return frame


def imu_data_gen():
    first = np.random.randint(0, 256, 18).tolist()
    second = np.random.randint(0, 256, 18).tolist()
    check_sum1 = [byte for byte in sum(first).to_bytes(2, "big")]
    check_sum2 = [byte for byte in sum(second).to_bytes(2, "big")]
    return first + check_sum1 + second + check_sum2


def create_random_data_file(n_frames=100):
    # Each data file begins with a simple header
    test_file = [0xbb] * 512

    # Now we generate our random frames and append them to our header
    for i in range(n_frames):
        test_file += create_random_frame(i)

    # Next we append a file footer
    test_file += [0xeb] * 512

    # Finally we return our new random file as a byte string
    return bytearray(test_file)  


if __name__ == "__main__":
    # This section was writen before `create_random_data_file` and doesn't need
    # to be updated to use this function. However, it essentially preforms the
    # same function plus some basic file writing...
    with open("Data/testy.bin", "wb") as f:
        test_file = [0xbb] * 512
        for i in range(100):
            test_file += create_random_frame(i)
        test_file += [0xeb] * 512
    
        f.write(bytearray(test_file))

