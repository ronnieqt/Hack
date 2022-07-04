"""
The main program that sets up and invokes the other modules.
"""

# %% import modules

from pathlib import Path

import argparse

from CompilationEngine import CompilationEngine

# %% command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument("src", help="Jack source file(s)")
options = parser.parse_args()

# %% main function

def _main():

    # cmd-line arg parsing
    src = Path(options.src)
    jack_files = [*src.glob("*.jack")] if src.is_dir() else [src]

    # process each jack file
    for jack_file in jack_files:
        engine = CompilationEngine(jack_file)
        engine.compile_class()
        engine.write_to_xml()

# %% call the main function

if __name__ == "__main__":
    _main()
