"""
This module ignores all comments and white space in the input stream and
enables accessing the input one token at a time. 
Also, it parses and provides the type of each token.
"""

# %% import libs

import re

from typing import List
from itertools import chain

from MyTypes import TokenType

# %% utils

def is_string_constant(block: str):
    return re.match(r"^\"[^\"\n]+\"$", block)


def is_identifier(block: str):
    return re.match(r"^[a-zA-Z_]\w*$", block)

# %% jack file processing

def process_line(line: str) -> str:
    line = re.sub("//.*$", "", line)
    line = line.strip()
    return re.findall(r'\S*".*"\S*|\S+', line)


def split_into_tokens(block: str) -> List[str]:
    patt = '([' + re.escape("".join(JackTokenizer.symbols)) + '])'
    return re.split(patt, block)


def process_code_block(block: str) -> List[str]:
    # when the given block is a stand-alone token
    if block in JackTokenizer.keywords \
        or block in JackTokenizer.symbols \
        or block.isdigit() \
        or is_string_constant(block) \
        or is_identifier(block):
        return [block]
    else:  # the given block is a collection of tokens
        return split_into_tokens(block)

def get_tokens(jack_file_path):
    # read the code as str
    with open(jack_file_path, 'r') as f:
        codes = f.read()
    # erase block comments
    # NOTE: *? will match in a non-greedy fasion
    codes = re.sub(r"/\*.*?\*/", " ", codes, flags=re.DOTALL)
    # split codes into lines
    lines = [process_line(line) for line in codes.split("\n")]
    # flatten processed lines into code blocks
    code_blocks = [*chain(*lines)]
    # split code blocks into tokens
    tokens = [process_code_block(block) for block in code_blocks]
    return [tkn for tkn in chain(*tokens) if tkn]

# %% class definition

class JackTokenizer:

    # static vars
    keywords = {
        "class", "constructor", "function", "method", "field", "static",
        "var", "int", "char", "boolean", "void", "true", "false", "null",
        "this", "let", "do", "if", "else", "while", "return"
    }
    symbols = {
        '{', '}', '(', ')', '[', ']', '.', ',', ';', 
        '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
    }

    def __init__(self, jack_file_path):
        self.tokens = get_tokens(jack_file_path)
        self.n_tokens = len(self.tokens)
        self.i_curr_token = -1
        self.curr_token = None  # initially, there is no current token

    def has_more_tokens(self):
        '''Are there more tokens in the input'''
        return self.i_curr_token < self.n_tokens - 1

    def advance(self):
        '''Gets the next token and makes it the current token'''
        assert self.has_more_tokens()
        self.i_curr_token += 1
        self.curr_token = self.tokens[self.i_curr_token]
    
    def token_lookahead(self):
        '''Checks the next token'''
        assert self.has_more_tokens()
        return self.tokens[self.i_curr_token+1]

    def token_type(self):
        '''Returns the type of the current token'''
        if self.curr_token is None:
            # when there is no current token
            return None
        elif self.curr_token in JackTokenizer.keywords:
            # keyword
            return TokenType.KEYWORD
        elif self.curr_token in JackTokenizer.symbols:
            # symbol
            return TokenType.SYMBOL
        elif self.curr_token.isdigit():
            # integer in range 0...32767
            if int(self.curr_token) <= 32767:
                return TokenType.INT_CONST
            else:
                raise OverflowError(f"[{self.curr_token}] is out-of-range!")
        elif is_string_constant(self.curr_token):
            # string: a sequence of chars not including " or \n
            return TokenType.STRING_CONST
        elif is_identifier(self.curr_token):
            # indentifier: a sequence of letters, digits, and _
            # (not starting with a digit)
            return TokenType.IDENTIFIER
        else:
            raise Exception(f"Unrecognized token: [{self.curr_token}]")

    def keyword(self):
        '''Returns the keyword which is the current token'''
        assert self.token_type() == TokenType.KEYWORD
        return self.curr_token  # TODO

    def symbol(self):
        '''Returns the character which is the current token'''
        assert self.token_type() == TokenType.SYMBOL
        return self.curr_token

    def identifier(self):
        '''Returns the string which is the current token'''
        assert self.token_type() == TokenType.IDENTIFIER
        return self.curr_token

    def int_val(self):
        '''Returns the integer value of the current token'''
        assert self.token_type() == TokenType.INT_CONST
        return int(self.curr_token)

    def string_val(self):
        '''Returns the string value of the current token'''
        assert self.token_type() == TokenType.STRING_CONST
        return self.curr_token.strip('"')

# %% testing

if __name__ == "__main__":
    print(get_tokens("./Compiler/tests/Square/SquareGame.jack"))
    print()
