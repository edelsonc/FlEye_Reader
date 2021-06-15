import sys
from chunker import Chunker
from framevalidator import FrameValidator
from framewriter import FrameWriter


if __name__ == "__main__":
    
    if len(sys.argv) >= 3:
        read_file, write_file = sys.argv[1], sys.argv[2]
    else:
        print("Missing required commandline arguments: read_file and write_file")
        sys.exit(1)

    try:
        chunker = Chunker(read_file)
    except FileNotFoundError:
        print("Provided read_file cannot be open. Check that the path to the read_file is correct")
        sys.exit(1)
