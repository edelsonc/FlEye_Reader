import sys, os
import click
from pathlib import Path
from datetime import datetime
from chunker import Chunker
from framevalidator import FrameValidator
from framewriter import FrameWriter
from configurations import configs

def create_log_paths(read_file):
    """
    Helper function to setup two log files for the current run of the data
    reading script.
    """
    logging_dir = Path(os.getcwd()) / "Log"
    
    read_file_tail = os.path.split(read_file)[1]

    current_time_str = datetime.now().strftime("%m_%d_%y-%H-%M-%S")
    read_log = logging_dir / (read_file_tail + current_time_str + ".log")
    return read_log


@click.command()
@click.argument('read_file')
@click.argument('write_file')
@click.option('--n_blocks', default=2 * 10**6, help='number of 512 byte blocks read into memeory in a single chunk')
def main(read_file, write_file, n_blocks):
    "Commandline program to validate and reformat data from the fly vision camera."
    #  creater an instance of Chunker with the read_file
    try:
        chunker = Chunker(read_file, block_number=n_blocks)
    except FileNotFoundError:
        print("Provided read_file cannot be open. Check that the path to the read_file is correct")
        sys.exit(1)

    # create log files for both FrameValidator and FrameWriter
    log_file = create_log_paths(read_file)

    framevalidator = FrameValidator(log_file, configs["header"], configs["footer"], configs["spacers"])
    framewriter = FrameWriter(configs["unpack_string"], write_file, log_file)

    while chunker.chunk_id != "END":
        chunk_id, chunk, byte_loc = chunker.next_chunk()
        split_chunk = Chunker.split(chunk, byte_loc, configs["header"])
        for frame_loc, frame in split_chunk:
            validated = framevalidator.validate(frame, chunk_id, frame_loc)
            if validated:
                framewriter.write(frame)

    chunker.close()
    framewriter.close()


if __name__ == "__main__":
  main() 
 
