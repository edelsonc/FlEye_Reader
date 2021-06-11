from random import getrandbits

def random_bytes(tmp_file):
    """Create a temporary file with random bytes"""
    with open(tmp_file, "wb") as t:
        data = bytes([getrandbits(8) for _ in range(1024 * 50)])
        t.write(data)       
    return data


def small_random_bytes(tmp_file):
    """Creates a small temporary file with random bytes"""
    with open(tmp_file, "wb") as t:
        data = bytes([getrandbits(8) for _ in range(1024 * 5)])
        t.write(data)
    return data

