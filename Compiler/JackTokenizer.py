"""
This module ignores all comments and white space in the input stream and
enables accessing the input one token at a time. 
Also, it parses and provides the type of each token.
"""

# %% import libs

import re
from tokenize import Token

from TokenTypes import TokenType

# %% file pre-processing

def preprocess(jack_file_path):
    with open(jack_file_path, 'r') as f:
        print(f.read())

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
        self.f_jack = open(jack_file_path, 'r')
        self.curr_token = None  # initially, there is no current token
        pass

    def has_more_tokens(self):
        '''Are there more tokens in the input'''
        pass

    def advance(self):
        '''Gets the next token and makes it the current token'''
        assert self.has_more_tokens()
        pass

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
        elif re.match(r"^\"[^\"\n]+\"$", self.curr_token):
            # string: a sequence of chars not including " or \n
            return TokenType.STRING_CONST
        elif re.match(r"^[^\d][\w\d_]*$", self.curr_token):
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
    preprocess("tests/ExpressionLessSquare/Main.jack")
