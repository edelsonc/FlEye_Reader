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


def find_all(string, substring):
    """
    Function to find all non-overlapping instances of a `substring` in `string`
    """
    start = 0
    matches = []
    while True:
        start = string.find(substring, start)
        if start == -1:
            return matches

        matches.append(start)
        start += len(substring)


def find_runs(chunker, configs):
    """
    Function to find data collection runs
    """
    run_starts = {}
    run_ends = {}
    while chunker.chunk_id != "END":
        chunk_id, chunk, byte_loc = chunker.next_chunk()
        starts = find_all(chunk, configs["run_start"])
        ends = find_all(chunk, configs["run_end"])

        for start in starts:
            run_start.add(start)

        for end in ends:
            run_ends.add(end)

    run_starts = sorted(list(run_starts))
    run_ends = sorted(list(run_ends))

    return match_ranges(run_starts, run_ends)


def match_ranges(starts, ends):
    runs = []
    for start in starts:
        for end in ends:
            if start < end:
                runs.append((start, end))
                break
    return runs


def intersections(intervals):
    ordered_intervals = sorted(intervals, key=lambda x: x[0])
    
    lower = ordered_intervals.pop(0)
    while ordered_intervals != []:
        for upper in ordered_intervals:
            if lower[1] > upper[0]:
                return True

        lower = ordered_intervals.pop(0)

    return False


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
        sys.exit(0)

    # create log files for both FrameValidator and FrameWriter
    log_file = create_log_paths(read_file)

    framevalidator = FrameValidator(log_file, configs["header"], configs["footer"], configs["spacers"])
    framewriter = FrameWriter(configs["unpack_string"], write_file, log_file)

    in_run = False
    run_id = 0
    while chunker.chunk_id != "END":
        chunk_id, chunk, byte_loc = chunker.next_chunk()
        split_chunk = Chunker.split(chunk, byte_loc, configs["header"])
        for frame_loc, frame in split_chunk:

            validated = framevalidator.validate(frame, chunk_id, frame_loc)
            if validated and in_run:
                framewriter.write(frame, run_id)

    chunker.close()
    framewriter.close()


if __name__ == "__main__":
  main() 
 
