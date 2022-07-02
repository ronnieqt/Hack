"""
The main program that sets up and invokes the other modules.
"""

# %% import modules

from pathlib import Path

import argparse

# %% command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument("src", help="Jack source file(s)")
options = parser.parse_args()

# %% process each jack file

def process_jack_file(jack_file: Path):
    pass

# %% main function

def _main():

    # cmd-line arg parsing
    src = Path(options.src)
    jack_files = [*src.glob("*.jack")] if src.is_dir() else [src]

    # process each jack file
    for jack_file in jack_files:
        process_jack_file(jack_file)

# %% call the main function

if __name__ == "__main__":
    _main()
