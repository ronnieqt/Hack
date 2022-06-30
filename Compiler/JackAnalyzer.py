"""
The main program that sets up and invokes the other modules.
"""

# %% import modules

from pathlib import Path

import argparse

from JackTokenizer import JackTokenizer

# %% command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument("src", help="Jack source file(s)")
options = parser.parse_args()

# %% main function

def _main():

    # cmd-line arg parsing
    src = Path(options.src)
    if not src.exists():
        print(f"[{src}] does not exist!")
        return
    elif src.is_dir():
        pass
    else:  # is_file
        pass
    print(src)

    tokenizer = JackTokenizer(src)

# %% call the main function

if __name__ == "__main__":
    _main()
