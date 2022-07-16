"""
The compilation engine gets its input from a JackTokenizer 
and emits its output to an output file.
"""

# %% import libs

from pathlib import Path
from collections import defaultdict

import xml.etree.ElementTree as ET

from utils import pretty_print, update_parent
from MyTypes import TokenType, VarKind, UsageType
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable

# %% VarKind Translation

VAR_KIND_TRANS = defaultdict(lambda: VarKind.NONE, {
    "static": VarKind.STATIC,
    "field" : VarKind.FIELD,
    "var"   : VarKind.VAR,
    "arg"   : VarKind.ARG
})

# %% CompilationEngine definition

class CompilationEngine:

    def __init__(self, jack_file_path: Path):
        '''Creates a new compilation engine.
        The next routine called must by compile_class().'''
        self.tknzr = JackTokenizer(jack_file_path)
        self.root = None    # root for the element tree
        self.parent = None  # the current parent node
        self.f_out_path = jack_file_path.with_suffix(".xml")
        self.tbl_class = SymbolTable()
        self.tbl_subroutine = SymbolTable()

    def compile_class(self):
        '''Compiles a complete class.'''
        # grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        # reset class-level symbol table
        self.tbl_class.reset()
        assert self.root is None
        self.parent = self.root = ET.Element("class")
        self.tknzr.advance()
        # expecting 'class'
        self.__add_keyword({"class"})
        # expecting className
        self.__add_identifier_cls(usage=UsageType.DECLARED)
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

    @update_parent("classVarDec")
    def compile_class_var_dec(self):
        '''Compiles a static variable declaration, or a field declaration.'''
        # grammar: ('static'|'field') type varName (',' varName)* ';'
        # expecting 'static' or 'field'
        kind = VAR_KIND_TRANS[self.__add_keyword({"static", "field"})]
        # expecting a type
        vtype = self.__add_type()
        # expecting varName (no advance)
        name = self.__get_identifier()
        # update the class level symbol table
        self.tbl_class.define(name, vtype, kind)
        # added to element tree and advance
        self.__add_identifier_var(usage=UsageType.DECLARED)
        # expecting (',' varName)*
        while self.tknzr.symbol() != ';':
            # expecting ','
            self.__add_symbol({','})
            # expecting varName (no advance)
            name = self.__get_identifier()
            # update the class level symbol table
            self.tbl_class.define(name, vtype, kind)
            # added to element tree and advance
            self.__add_identifier_var(usage=UsageType.DECLARED)
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("subroutineDec")
    def compile_subroutine(self):
        '''Compiles a complete method, function, or ctor.'''
        # grammar: ('constructor'|'function'|'method') ('void'|type) subroutineName
        #          '(' parameterList ')' subroutineBody
        # reset subroutine-level symbol table
        self.tbl_subroutine.reset()
        # expecting keyword 'constructor' or 'function' or 'method'
        self.__add_keyword({"constructor", "function", "method"})
        # expecting 'void' or type
        try:  # 'void'
            self.__add_keyword({"void"})
        except:  # type
            self.__add_type()
        # expecting a subrountineName
        self.__add_identifier_sub(usage=UsageType.DECLARED)
        # expecting '('
        self.__add_symbol({'('})
        # expecting parameterList
        self.compile_parameter_list()
        # expecting ')'
        self.__add_symbol({')'})
        # expecting subrountineBody
        self.compile_subroutine_body()

    @update_parent("parameterList")
    def compile_parameter_list(self):
        '''Compiles a (possibly empty) parameter list.
        Does not handle the enclosing parentheses tokens ( and ).'''
        # grammar: ((type varName) (',' type varName)*)?
        # empty parameter list
        if self.tknzr.token_type() == TokenType.SYMBOL:
            self.parent.text = " "
            return
        # non-empty parameter list
        while True:
            # expecting type
            vtype = self.__add_type()
            # expecting varName (no advance)
            name = self.__get_identifier()
            # update the subroutine level symbol table
            self.tbl_subroutine.define(name, vtype, VarKind.ARG)
            # added to element tree and advance
            self.__add_identifier_var(usage=UsageType.DECLARED)
            # expecting a symbol (either ',' or ')')
            if self.tknzr.symbol() == ',':
                self.__add_symbol({','})
            else:
                break

    @update_parent("subroutineBody")
    def compile_subroutine_body(self):
        '''Compiles a subroutine's body.'''
        # grammar: '{' varDec* statements '}'
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting varDec*
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() != "var":
                break
            self.compile_var_dec()
        # expecting statements
        self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})

    @update_parent("varDec")
    def compile_var_dec(self):
        '''Compiles a var declaration.'''
        # grammar: 'var' type varName (',' varName)* ';'
        # expecting 'var'
        kind = VAR_KIND_TRANS[self.__add_keyword({"var"})]
        # expecting type
        vtype = self.__add_type()
        # expecting varName (no advance)
        name = self.__get_identifier()
        # update the subroutine level symbol table
        self.tbl_subroutine.define(name, vtype, kind)
        # added to element tree and advance
        self.__add_identifier_var(usage=UsageType.DECLARED)
        # expecting a symbol (either ',' or ';')
        while self.tknzr.symbol() != ';':
            # expecting ','
            self.__add_symbol({','})
            # expecting varName (no advance)
            name = self.__get_identifier()
            # update the subroutine level symbol table
            self.tbl_subroutine.define(name, vtype, kind)
            # added to element tree and advance
            name = self.__add_identifier_var(usage=UsageType.DECLARED)
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("statements")
    def compile_statements(self):
        '''Compiles a sequence of statements.
        Does not handle the enclosing curly bracket tokens { and }.'''
        # grammar: statement*
        # statement: let, if, while, do, return
        any_statement = False
        while self.tknzr.token_type() != TokenType.SYMBOL:
            # expecting a statement
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
            any_statement = True
        if not any_statement:
            self.parent.text = " "

    @update_parent("letStatement")
    def compile_let(self):
        '''Compiles a let statement.'''
        # grammar: 'let' varName ('['expression']')? '=' expression ';'
        # expecting 'let'
        self.__add_keyword({"let"})
        # expecting varName
        self.__add_identifier_var()
        # expecting ('['expression']')?
        if self.tknzr.symbol() == '[':
            self.__add_symbol({'['})
            self.compile_expression()
            self.__add_symbol({']'})
        # expecting '='
        self.__add_symbol({'='})
        # expecting an expression
        self.compile_expression()
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("ifStatement")
    def compile_if(self):
        '''Compiles an if statement, possibly with a trailing else clause.'''
        # grammar: 'if' '(' expression ')' '{' statements '}' 
        #         ('else' '{' statements '}')?
        # expecting 'if'
        self.__add_keyword({'if'})
        # expecting '('
        self.__add_symbol({'('})
        # expecting an expression
        self.compile_expression()
        # expecting ')'
        self.__add_symbol({')'})
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting statements
        self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})
        # check whether we have an else clause
        if self.tknzr.token_type() == TokenType.KEYWORD and \
            self.tknzr.keyword() == "else":
            # ('else' '{' statements '}')?
            self.__add_keyword({"else"})
            self.__add_symbol({'{'})
            self.compile_statements()
            self.__add_symbol({'}'})

    @update_parent("whileStatement")
    def compile_while(self):
        '''Compiles a while statement.'''
        # grammar: 'while' '(' expression ')' '{' statements '}'
        # expecting 'while'
        self.__add_keyword({'while'})
        # expecting '('
        self.__add_symbol({'('})
        # expecting an expression
        self.compile_expression()
        # expecting ')'
        self.__add_symbol({')'})
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting statements
        self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})

    @update_parent("doStatement")
    def compile_do(self):
        '''Compiles a do statement.'''
        # grammar: 'do' subroutineCall ';'
        # expecting 'do'
        self.__add_keyword({"do"})
        # expecting subroutineCall
        self.__compile_subroutine_call()
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("returnStatement")
    def compile_return(self):
        '''Compiles a return statement.'''
        # grammar: 'return' expression? ';'
        # expecting 'return'
        self.__add_keyword({"return"})
        if self.tknzr.token_type() != TokenType.SYMBOL \
            or self.tknzr.symbol() != ';':
            # expecting an expression
            self.compile_expression()
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("expression")
    def compile_expression(self):
        '''Compiles an expression.'''
        # grammar: term (op term)*
        self.compile_term()
        while self.tknzr.token_type() == TokenType.SYMBOL \
            and self.tknzr.symbol() in {'+','-','*','/','&','|','<','>','='}:
            self.__add_symbol()
            self.compile_term()
    
    @update_parent("term")
    def compile_term(self):
        '''Compiles a term.
        If the current token is an identifier, the routine must resolve it
            into a variable, an array element, or a subrountine call.
        A single lookahead token, which may be [, (, or . suffices to
            distinguish between the possibilities.
        Any other token is not part of this term and should not be advanced over.'''
        # grammar: integerConstant | stringConstant | keywordConstant | 
        #          varName | varName '[' expression ']' | subroutineCall |
        #          '(' expression ')' | (unaryOp term) 
        if self.tknzr.token_type() == TokenType.INT_CONST:
            # integer
            elem = ET.SubElement(self.parent, "integerConstant")
            elem.text = str( self.tknzr.int_val() )
            self.tknzr.advance()
        elif self.tknzr.token_type() == TokenType.STRING_CONST:
            # string
            elem = ET.SubElement(self.parent, "stringConstant")
            elem.text = self.tknzr.string_val()
            self.tknzr.advance()
        elif self.tknzr.token_type() == TokenType.KEYWORD:
            # keyword
            self.__add_keyword({"true","false","null","this"})
        elif self.tknzr.token_type() == TokenType.IDENTIFIER:
            # varName | varName '[' expression ']' | subroutineCall
            if self.tknzr.peek_next() == '[':
                # varName '[' expression ']'
                self.__add_identifier_var()
                self.__add_symbol({'['})
                self.compile_expression()
                self.__add_symbol({']'})
            elif self.tknzr.peek_next() in {'(', '.'}:
                # subroutineCall
                self.__compile_subroutine_call()
            else:
                # varName
                self.__add_identifier_var()
        else:
            # '(' expression ')' | (unaryOp term) 
            if self.tknzr.symbol() == '(':
                # '(' expression ')'
                self.__add_symbol({'('})
                self.compile_expression()
                self.__add_symbol({')'})
            else:
                # (unaryOp term) 
                self.__add_symbol({'-','~'})
                self.compile_term()

    @update_parent("expressionList")
    def compile_expression_list(self) -> int:
        '''Compiles a (possibly empty) comma-separated list of expressions.
        Returns the number of expressions in the list.'''
        # grammar: (expression (',' expression)* )?
        n_expr = 0
        while self.tknzr.token_type() != TokenType.SYMBOL or \
            self.tknzr.symbol() != ')':
            self.compile_expression(); n_expr += 1
            if self.tknzr.token_type() == TokenType.SYMBOL and \
                self.tknzr.symbol() == ',':
                self.__add_symbol()
        if not n_expr:
            self.parent.text = " "
        return n_expr
    
    def write_to_xml(self):
        '''Writes the program structure to xml.'''
        if self.root is not None:
            pretty_print(self.root)
            ET.ElementTree(self.root).write(self.f_out_path)
            print(f"XML file written to [{self.f_out_path}]")
    
    def __compile_subroutine_call(self):
        # subroutineCall
        # grammer: (className|varName) '.' subroutineName '(' expressionList ')' |
        #                                  subroutineName '(' expressionList ')'
        if self.tknzr.peek_next() == '.':
            # expecting (className|varName) '.'
            try:
                self.__add_identifier_var()
            except:
                self.__add_identifier_cls()
            self.__add_symbol({'.'})
        # expecting subroutineName '(' expressionList ')'
        self.__add_identifier_sub()
        self.__add_symbol({'('})
        self.compile_expression_list()
        self.__add_symbol({')'})
    
    def __add_keyword(self, allow=JackTokenizer.keywords, advance=True):
        keyword = self.tknzr.keyword()
        assert keyword in allow, f"keyword [{keyword}] is not in {allow}"
        elem = ET.SubElement(self.parent, "keyword")
        elem.text = keyword
        if advance:
            self.tknzr.advance()
        return keyword
    
    def __add_symbol(self, allow=JackTokenizer.symbols, advance=True):
        symbol = self.tknzr.symbol()
        assert symbol in allow, f"symbol [{symbol}] is not in {allow}"
        elem = ET.SubElement(self.parent, "symbol")
        elem.text = symbol
        if advance: 
            self.tknzr.advance()
        return symbol
    
    def __get_identifier(self):
        return self.tknzr.identifier()

    def __add_identifier_var(self, usage=UsageType.USED, advance=True):
        # read the variable name
        name = self.__get_identifier()
        # symbol table look up
        if self.tbl_subroutine.contains(name):
            category = self.tbl_subroutine.kind_of(name).name
            index = self.tbl_subroutine.index_of(name)
        elif self.tbl_class.contains(name):
            category = self.tbl_class.kind_of(name).name
            index = self.tbl_class.index_of(name)
        else:
            raise NameError(f"Undefined Variable: {name}")
        # add identifier to the element tree
        elem = ET.SubElement(self.parent, "identifier")
        # name
        sub_elem = ET.SubElement(elem, "name")
        sub_elem.text = name
        # category (field, static, var, arg)
        sub_elem = ET.SubElement(elem, "category")
        sub_elem.text = category
        # index
        sub_elem = ET.SubElement(elem, "index")
        sub_elem.text = str(index)
        # usage
        sub_elem = ET.SubElement(elem, "usage")
        sub_elem.text = usage.name
        if advance:
            self.tknzr.advance()
        return name

    def __add_identifier(self, usage, category, advance):
        # read the identifier
        identifier = self.__get_identifier()
        # add identifier to the element tree
        elem = ET.SubElement(self.parent, "identifier")
        # name
        sub_elem = ET.SubElement(elem, "name")
        sub_elem.text = identifier
        # category
        sub_elem = ET.SubElement(elem, "category")
        sub_elem.text = category
        # usage
        sub_elem = ET.SubElement(elem, "usage")
        sub_elem.text = usage.name
        if advance:
            self.tknzr.advance()
        return identifier

    def __add_identifier_cls(self, usage=UsageType.USED, advance=True):
        return self.__add_identifier(usage, "CLASS", advance)
    
    def __add_identifier_sub(self, usage=UsageType.USED, advance=True):
        return self.__add_identifier(usage, "SUBROUTINE", advance)

    def __add_type(self, advance=True):
        # expecting 'int' or 'char' or 'boolean' or className
        try:  # 'int' | 'char' | 'boolean'
            t = self.__add_keyword({"int", "char", "boolean"}, advance)
        except:  # className
            t = self.__add_identifier_cls(advance=advance)
        return t
