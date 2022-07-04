"""
The compilation engine gets its input from a JackTokenizer 
and emits its output to an output file.
"""

# %% import libs

from pathlib import Path

import xml.etree.ElementTree as ET

from utils import pretty_print
from TokenTypes import TokenType
from JackTokenizer import JackTokenizer

# %% CompilationEngine definition

class CompilationEngine:

    def __init__(self, jack_file_path: Path):
        '''Creates a new compilation engine.
        The next routine called must by compile_class().'''
        self.tknzr = JackTokenizer(jack_file_path)
        self.root = None    # root for the element tree
        self.parent = None  # the current parent node
        self.f_out_path = jack_file_path.with_suffix(".xml")

    def compile_class(self):
        '''Compiles a complete class.'''
        # grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        assert self.root is None
        self.parent = self.root = ET.Element("class")
        self.tknzr.advance()
        # expecting 'class'
        self.__add_keyword({"class"})
        # expecting className
        self.__add_identifier()
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting classVarDec*
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() not in {"static", "field"}:
                break
            self.compile_class_var_dec()
        # expecting subrountineDec*
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() not in {"constructor", "function", "method"}:
                break
            self.compile_subroutine()
        # expecting '}'
        self.__add_symbol({'}'}, advance=False)

    def compile_class_var_dec(self):
        '''Compiles a static variable declaration, or a field declaration.'''
        # grammar: ('static'|'field') type varName (',' varName)* ';'
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "classVarDec")
        # expecting 'static' or 'field'
        self.__add_keyword({"static", "field"})
        # expecting a type
        self.__add_type()
        # expecting varName
        self.__add_identifier()
        # expecting (',' varName)*
        while self.tknzr.symbol() != ';':
            # expecting ','
            self.__add_symbol({','})
            # expecting varName
            self.__add_identifier()
        # expecting ';'
        self.__add_symbol({';'})
        # reset self.parent
        self.parent = parent

    def compile_subroutine(self):
        '''Compiles a complete method, function, or ctor.'''
        # grammar: ('constructor'|'function'|'method') ('void'|type) subroutineName
        #          '(' parameterList ')' subroutineBody
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "subroutineDec")
        # expecting keyword 'constructor' or 'function' or 'method'
        self.__add_keyword({"constructor", "function", "method"})
        # expecting 'void' or type
        try:  # 'void'
            self.__add_keyword({"void"})
        except:  # type
            self.__add_type()
        # expecting a subrountineName
        self.__add_identifier()
        # expecting '('
        self.__add_symbol({'('})
        # expecting parameterList
        self.compile_parameter_list()
        # expecting ')'
        self.__add_symbol({')'})
        # expecting subrountineBody
        self.compile_subroutine_body()
        # reset self.parent
        self.parent = parent

    def compile_parameter_list(self):
        '''Compiles a (possibly empty) parameter list.
        Does not handle the enclosing parentheses tokens ( and ).'''
        # grammar: ((type varName) (',' type varName)*)?
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "parameterList")
        # empty parameter list
        if self.tknzr.token_type() == TokenType.SYMBOL:
            self.parent.text = " "
            self.parent = parent
            return
        # non-empty parameter list
        while True:
            # expecting type
            self.__add_type()
            # expecting varName
            self.__add_identifier()
            # expecting a symbol (either ',' or ')')
            if self.tknzr.symbol() == ',':
                self.__add_symbol({','})
            else:
                break
        # reset self.parent
        self.parent = parent

    def compile_subroutine_body(self):
        '''Compiles a subroutine's body.'''
        # grammar: '{' varDec* statements '}'
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "subroutineBody")
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting varDec*
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() != "var":
                break
            self.compile_var_dec()
        # expecting statements
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() not in {"let", "if", "while", "do", "return"}:
                break
            self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})
        # reset self.parent
        self.parent = parent

    def compile_var_dec(self):
        '''Compiles a var declaration.'''
        # grammar: 'var' type varName (',' varName)* ';'
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "varDec")
        # expecting 'var'
        self.__add_keyword({"var"})
        # expecting type
        self.__add_type()
        # expecting varName
        self.__add_identifier()
        # expecting a symbol (either ',' or ';')
        while self.tknzr.symbol() != ';':
            # expecting ','
            self.__add_symbol({','})
            # expecting varName
            self.__add_identifier()
        # expecting ';'
        self.__add_symbol({';'})
        # reset self.parent
        self.parent = parent

    def compile_statements(self):
        '''Compiles a sequence of statements.
        Does not handle the enclosing curly bracket tokens { and }.'''
        # grammar: statement*
        # statement: let, if, while, do, return
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "statements")
        # expecting a statement
        while self.tknzr.token_type() != TokenType.SYMBOL:
            keyword = self.tknzr.keyword()
            if keyword == "let":
                self.compile_let()
            elif keyword == "if":
                self.compile_if()
            elif keyword == "while":
                self.compile_while()
            elif keyword == "do":
                self.compile_do()
            elif keyword == "return":
                self.compile_return()
            else:
                raise Exception(f"Unrecognized keyword: [{keyword}]")
        # reset self.parent
        self.parent = parent

    def compile_let(self):
        '''Compiles a let statement.'''
        # grammar: 'let' varName ('['expression']')? '=' expression ';'
        # backup self.parent
        parent = self.parent
        # update self.parent
        self.parent = ET.SubElement(self.parent, "letStatement")
        # expecting 'let'
        self.__add_keyword({"let"})
        # expecting varName
        self.__add_identifier()
        # expecting ('['expression']')?
        # TODO
        # expecting '='
        self.__add_symbol({'='})
        # expecting expression
        # TODO
        self.__add_identifier()  # TODO: remove this line
        # expecting ';'
        self.__add_symbol({';'})
        # reset self.parent
        self.parent = parent

    def compile_if(self):
        '''Compiles an if statement, possibly with a trailing else clause.'''
        pass

    def compile_while(self):
        '''Compiles a while statement.'''
        pass

    def compile_do(self):
        '''Compiles a do statement.'''
        pass

    def compile_return(self):
        '''Compiles a return statement.'''
        pass

    def compile_expression(self):
        '''Compiles an expression.'''
        pass

    def compile_term(self):
        '''Compiles a term.
        If the current token is an identifier, the routine must resolve it
            into a variable, an array element, or a subrountine call.
        A single lookahead token, which may be [, (, or . suffices to
            distinguish between the possibilities.
        Any other token is not part of this term and should not be advanced over.'''
        pass

    def compile_expression_list(self) -> int:
        '''Compiles a (possibly empty) comma-separated list of expressions.
        Returns the number of expressions in the list.'''
        pass
    
    def write_to_xml(self):
        '''Writes the program structure to xml.'''
        if self.root is not None:
            pretty_print(self.root)
            ET.ElementTree(self.root).write(self.f_out_path)
            print(f"XML file written to [{self.f_out_path}]")
    
    def __add_keyword(self, allow=JackTokenizer.keywords, advance=True):
        keyword = self.tknzr.keyword()
        assert keyword in allow, f"keyword [{keyword}] is not in {allow}"
        elem = ET.SubElement(self.parent, "keyword")
        elem.text = keyword
        if advance:
            self.tknzr.advance()
    
    def __add_symbol(self, allow=JackTokenizer.symbols, advance=True):
        symbol = self.tknzr.symbol()
        assert symbol in allow, f"symbol [{symbol}] is not in {allow}"
        elem = ET.SubElement(self.parent, "symbol")
        elem.text = symbol
        if advance: 
            self.tknzr.advance()

    def __add_identifier(self, advance=True):
        elem = ET.SubElement(self.parent, "identifier")
        elem.text = self.tknzr.identifier()
        if advance:
            self.tknzr.advance()

    def __add_type(self, advance=True):
        # expecting 'int' or 'char' or 'boolean' or className
        try:  # 'int' | 'char' | 'boolean'
            self.__add_keyword({"int", "char", "boolean"}, advance)
        except:  # className
            self.__add_identifier(advance)
