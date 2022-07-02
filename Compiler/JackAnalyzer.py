"""
The main program that sets up and invokes the other modules.
"""

# %% import modules

from pathlib import Path

import argparse
import xml.etree.ElementTree as ET

from TokenTypes import TokenType
from JackTokenizer import JackTokenizer

from utils import pretty_print

# %% command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument("src", help="Jack source file(s)")
options = parser.parse_args()

# %% process one jack file

def process_jack_file(jack_file_path: Path):

    tknzr = JackTokenizer(jack_file_path)

    tokens = ET.Element("tokens")

    while tknzr.has_more_tokens():

        tknzr.advance()

        if tknzr.token_type() == TokenType.KEYWORD:
            elem = ET.SubElement(tokens, "keyword")
            elem.text = tknzr.keyword()
        elif tknzr.token_type() == TokenType.SYMBOL:
            elem = ET.SubElement(tokens, "symbol")
            elem.text = tknzr.symbol()
        elif tknzr.token_type() == TokenType.INT_CONST:
            elem = ET.SubElement(tokens, "integerConstant")
            elem.text = str(tknzr.int_val())
        elif tknzr.token_type() == TokenType.STRING_CONST:
            elem = ET.SubElement(tokens, "stringConstant")
            elem.text = tknzr.string_val()
        elif tknzr.token_type() == TokenType.IDENTIFIER:
            elem = ET.SubElement(tokens, "identifier")
            elem.text = tknzr.identifier()
        else:
            raise Exception(f"Unrecognized Token Type: [{tknzr.token_type()}]")
    
    pretty_print(tokens)

    xml_file_path = jack_file_path.with_name(f"{jack_file_path.stem}T.xml")
    ET.ElementTree(tokens).write(xml_file_path)

# %% main function

def _main():

    # cmd-line arg parsing
    src = Path(options.src)
    if not src.exists():
        print(f"[{src}] does not exist!")
        return
    elif src.is_dir():
        for jack_file in src.glob("*.jack"):
            process_jack_file(jack_file)
    else:  # is_file
        process_jack_file(src)

# %% call the main function

if __name__ == "__main__":
    _main()
