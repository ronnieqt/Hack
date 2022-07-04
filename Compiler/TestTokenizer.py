# %% import libs

from pathlib import Path

import argparse
import xml.etree.ElementTree as ET

from utils import pretty_print
from TokenTypes import TokenType
from JackTokenizer import JackTokenizer

# %% test implementation of the tokenizer

def test_tokenizer(jack_file_path: Path):

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
    
    pretty_print(tokens, indent="")

    xml_file_path = jack_file_path.with_name(f"{jack_file_path.stem}T.xml")
    ET.ElementTree(tokens).write(xml_file_path)

# %% main function for testing

def _main(src: Path):

    jack_files = [*src.glob("*.jack")] if src.is_dir() else [src]
    for jack_file in jack_files:
        test_tokenizer(jack_file)

# %% calling the main function

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Jack source file(s)")
    options = parser.parse_args()

    _main(Path(options.src))
