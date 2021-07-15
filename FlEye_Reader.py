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
@click.option('--n_blocks', default=10**6, help='number of 512 byte blocks read into memeory in a single chunk')
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

    # we need to keep track of when we're in a data run; these two variables
    # will be used to determine when to write frames and how to label runs
    in_run = False
    run_id = 0
    while chunker.chunk_id != "END":
        chunk_id, chunk, byte_loc = chunker.next_chunk()
        split_chunk = Chunker.split(chunk, byte_loc, configs["header"])
        for frame_loc, frame in split_chunk:
            # TODO determine if the following should be at the "chunk" level
            # if configs["run_start"] in frame:
            #     in_run = True
            #     run_id += 1
            # elif configs["run_end"] in frame:
            #     in_run = False
            # elif (configs["run_start"] in frame) and (configs["run_end"] in frame):
            #     # This is the case where you have a block that contains both a
            #     # start run and end run delimiter. This occurs when you have
            #     # multiple runs and you get a frame that's just the two
            #     # delimiters back to back.
            #     start_pos, end_pos = frame.find(configs["run_start"]), frame.find(configs["run_end"])
            #     if start_pos < end_pos:
            #         in_run = False
            #     else:
            #         in_run = True
            #         run_id += 1

            validated = framevalidator.validate(frame, chunk_id, frame_loc)
            if validated and in_run:
                framewriter.write(frame, run_id)

    chunker.close()
    framewriter.close()


if __name__ == "__main__":
  main() 
 
