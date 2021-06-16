import sys, os
from pathlib import Path
from datetime import datetime
from chunker import Chunker
from framevalidator import FrameValidator
from framewriter import FrameWriter
from configurations import configs

def create_log_paths(read_file, write_file):
    """
    Helper function to setup two log files for the current run of the data
    reading script.
    """
    logging_dir = Path(os.getcwd()) / "Log"
    
    read_file_tail = os.path.split(read_file)[1]
    write_file_tail = os.paht.split(write_file)[1]

    current_time_str = datetime.now().strftime("%m_%d_%y-%H-%M-%S")
    read_log = logging_dir / (read_file_tail + current_time_str + ".log")
    write_log = logging_dir / (write_file_tail + current_time_str + ".log")
    return read_log, write_log 


if __name__ == "__main__":
   
    # begin by grabbing the read file for the data and write file 
    if len(sys.argv) >= 3:
        read_file, write_file = sys.argv[1], sys.argv[2]
    else:
        print("Missing required commandline arguments: read_file and write_file")
        sys.exit(1)

    #  creater an instance of Chunker with the read_file
    try:
        chunker = Chunker(read_file)
    except FileNotFoundError:
        print("Provided read_file cannot be open. Check that the path to the read_file is correct")
        sys.exit(1)

    # create log files for both FrameValidator and FrameWriter
    read_log, write_log = create_log_paths(read_file, write_file)

    framevalidator = FrameValidator(read_log, configs["header"], configs["footer"], configs["spacers"])
    framewriter = FrameWriter(configs["unpack_string"], write_file, write_log)

    try:
        while chunker.chunk_id != "END":
            chunk_id, chunk, byte_loc = chunker.next_chunk()

