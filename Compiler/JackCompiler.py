"""
This module drives the compilation process.
It operates on either a file name of the form Xxx.jack or
    on a folder name containing one or more such files.
For each source Xxx.jack file, the program
    1. creates a JackTokenizer from the Xxx.jack input file;
    2. creates an output file named Xxx.vm; and
    3. uses a CompilationEngine, a SymbolTable, and a VMWriter
       for parsing the input file and emitting the translated
       VM code into the output file.
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
        engine.close()

# %% call the main function

if __name__ == "__main__":
    _main()
