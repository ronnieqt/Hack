"""
The compilation engine gets its input from a JackTokenizer 
and emits its output to an output file.
"""

# %% import libs

from pathlib import Path
from collections import defaultdict

import xml.etree.ElementTree as ET

from utils import pretty_print, update_parent
from MyTypes import TokenType, VarKind, UsageType, SegmentType
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

# %% VarKind Translation

VAR_KIND_TRANS = defaultdict(lambda: VarKind.NONE, {
    "static": VarKind.STATIC,
    "field" : VarKind.FIELD,
    "var"   : VarKind.VAR,
    "arg"   : VarKind.ARG
})

VAR_KIND_TO_SEG = {
    VarKind.STATIC: SegmentType.STATIC,
    VarKind.FIELD : SegmentType.THIS,
    VarKind.ARG   : SegmentType.ARGUMENT,
    VarKind.VAR   : SegmentType.LOCAL
}

# %% CompilationEngine definition

class CompilationEngine:

    def __init__(self, jack_file_path: Path):
        '''Creates a new compilation engine.
        Note: The next routine called must by compile_class().
              Assume that: 1 Jack file contains only 1 class.
        '''
        self.jack_file_path = jack_file_path
        self.tknzr = JackTokenizer(self.jack_file_path)
        self.root = None                     # root for the element tree
        self.parent = None                   # the current parent node
        self.tbl_class = SymbolTable()       # class-level symbol table
        self.tbl_subroutine = SymbolTable()  # subroutine-level symbol table
        self.vm_writer = VMWriter(self.jack_file_path.with_suffix(".vm"))
        self.cls_name = ""                   # name of this class
        self.n_while = 0                     # counter of while statement
        # init a function level static variables
        CompilationEngine.compile_if.n_if = 0
        CompilationEngine.compile_while.n_while = 0
    
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
        self.cls_name = self.__add_identifier_cls(usage=UsageType.DECLARED)
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
        # expecting keyword 'constructor' or 'method', or 'function'
        keyword = self.__add_keyword({"constructor", "method", "function"})
        # reset subroutine-level symbol table
        self.tbl_subroutine.reset(keyword=="method")
        # expecting 'void' or type
        try:  # 'void'
            self.__add_keyword({"void"})
        except:  # type
            self.__add_type()
        # expecting a subrountineName
        sub_name = self.__add_identifier_sub(usage=UsageType.DECLARED)
        # expecting '('
        self.__add_symbol({'('})
        # expecting parameterList
        self.compile_parameter_list()
        # expecting ')'
        self.__add_symbol({')'})
        # expecting subrountineBody
        self.compile_subroutine_body(keyword, sub_name)

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
    def compile_subroutine_body(self, keyword, sub_name):
        '''Compiles a subroutine's body.'''
        # grammar: '{' varDec* statements '}'
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting varDec*
        while self.tknzr.token_type() != TokenType.SYMBOL:
            if self.tknzr.keyword() != "var":
                break
            self.compile_var_dec()
        # write the subroutine declaration
        self.vm_writer.write_function(
            self.cls_name + '.' + sub_name,             # function name
            self.tbl_subroutine.var_count(VarKind.VAR)  # number of local variables
        )
        # if the subroutine is a ctor, then allocate memory
        if keyword == "constructor":
            n_fields = self.tbl_class.var_count(VarKind.FIELD)
            self.vm_writer.write_push(SegmentType.CONSTANT, n_fields)
            # arrange a memory block to store the new object's fields
            self.vm_writer.write_call("Memory.alloc", 1)
            # returns its base address to the caller
            self.vm_writer.write_pop(SegmentType.POINTER, 0)  # pop to this
        elif keyword == "method":
            # in a method, pop the first arg to this
            self.vm_writer.write_push(SegmentType.ARGUMENT, 0)
            self.vm_writer.write_pop(SegmentType.POINTER, 0)
        else:  # function
            pass
        # expecting statements
        self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})
        # reset n_if and n_while counters
        CompilationEngine.compile_if.n_if = 0
        CompilationEngine.compile_if.n_while = 0

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
        var_name = self.__add_identifier_var()
        var_prop = self.__look_up_in_symbol_table(var_name)
        # check whether this is a variable or an array assignment
        is_array_assignment = self.tknzr.symbol() == '['
        # array assignment
        if is_array_assignment:
            # expecting ('['expression']')?
            self.__add_symbol({'['})
            self.compile_expression()
            self.__add_symbol({']'})
            # put the value of varName at the stack's top
            self.vm_writer.write_push(VAR_KIND_TO_SEG[var_prop.kind], var_prop.index)
            # calc (varName + expression)
            self.vm_writer.write_arithmetic("add")
            # expecting '='
            self.__add_symbol({'='})
            # expecting an expression
            self.compile_expression()
            # save the value of the rhs expression
            self.vm_writer.write_pop(SegmentType.TEMP, 0)
            # assign value of the rhs expression to array
            self.vm_writer.write_pop(SegmentType.POINTER, 1)  # that = varName + expression
            self.vm_writer.write_push(SegmentType.TEMP, 0)    # put value of rhs at the stack's top
            self.vm_writer.write_pop(SegmentType.THAT, 0)     # *(varName+expression) = rhs's value
        else:  # variable assignment
            # expecting '='
            self.__add_symbol({'='})
            # expecting an expression
            self.compile_expression()
            # assign value of the rhs expression to the variable varName
            self.vm_writer.write_pop(VAR_KIND_TO_SEG[var_prop.kind], var_prop.index)
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("ifStatement")
    def compile_if(self):
        '''Compiles an if statement, possibly with a trailing else clause.'''
        # grammar: 'if' '(' expression ')' '{' statements '}' 
        #         ('else' '{' statements '}')?
        n_if = CompilationEngine.compile_if.n_if
        CompilationEngine.compile_if.n_if += 1
        # expecting 'if'
        self.__add_keyword({'if'})
        # expecting '('
        self.__add_symbol({'('})
        # expecting an expression
        self.compile_expression()
        # expecting ')'
        self.__add_symbol({')'})
        # write if-goto IF_TRUE; goto IF_FALSE
        self.vm_writer.write_if(f"IF_TRUE{n_if}")
        self.vm_writer.write_goto(f"IF_FALSE{n_if}")
        self.vm_writer.write_label(f"IF_TRUE{n_if}")
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting statements
        self.compile_statements()
        # expecting '}'
        self.__add_symbol({'}'})
        # check whether we have a else block or not
        has_else = self.tknzr.token_type() == TokenType.KEYWORD and \
            self.tknzr.keyword() == "else"
        # write goto IF_END
        if has_else:
            self.vm_writer.write_goto(f"IF_END{n_if}")
        # write label IF_FALSE
        self.vm_writer.write_label(f"IF_FALSE{n_if}")
        # check whether we have an 'else' clause
        if has_else:
            # ('else' '{' statements '}')?
            self.__add_keyword({"else"})
            self.__add_symbol({'{'})
            self.compile_statements()
            self.__add_symbol({'}'})
            # write label IF_END
            self.vm_writer.write_label(f"IF_END{n_if}")

    @update_parent("whileStatement")
    def compile_while(self):
        '''Compiles a while statement.'''
        # grammar: 'while' '(' expression ')' '{' statements '}'
        n_while = CompilationEngine.compile_while.n_while
        CompilationEngine.compile_while.n_while += 1
        # expecting 'while'
        self.__add_keyword({'while'})
        # write label WHILE_EXP
        self.vm_writer.write_label(f"WHILE_EXP{n_while}")
        # expecting '('
        self.__add_symbol({'('})
        # expecting an expression
        self.compile_expression()
        # expecting ')'
        self.__add_symbol({')'})
        # write not; if-goto WHILE_END
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(f"WHILE_END{n_while}")
        # expecting '{'
        self.__add_symbol({'{'})
        # expecting statements
        self.compile_statements()
        # write goto WHILE_EXP
        self.vm_writer.write_goto(f"WHILE_EXP{n_while}")
        # expecting '}'
        self.__add_symbol({'}'})
        # write label WHILE_END
        self.vm_writer.write_label(f"WHILE_END{n_while}")

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
        # pop the return value to temp 0 (ignoring the return value)
        self.vm_writer.write_pop(SegmentType.TEMP, 0)

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
        else:  # return from a void function
            self.vm_writer.write_push(SegmentType.CONSTANT, 0)
        # write return
        self.vm_writer.write_return()
        # expecting ';'
        self.__add_symbol({';'})

    @update_parent("expression")
    def compile_expression(self):
        '''Compiles an expression.'''
        # grammar: term (op term)*
        self.compile_term()
        while self.tknzr.token_type() == TokenType.SYMBOL \
            and self.tknzr.symbol() in {'+','-','*','/','&','|','<','>','='}:
            op = self.__add_symbol()
            self.compile_term()
            # output op
            if op in VMWriter.al_op2cmd.keys():
                self.vm_writer.write_arithmetic(VMWriter.al_op2cmd[op])
            else:  # {'*','/'}
                self.vm_writer.write_call(VMWriter.al_op2func[op], 2)
    
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
            val = self.tknzr.int_val()
            elem.text = str(val)
            self.tknzr.advance()
            # output "push c"
            self.vm_writer.write_push(SegmentType.CONSTANT, val)
        elif self.tknzr.token_type() == TokenType.STRING_CONST:
            # string
            txt = self.tknzr.string_val()
            elem = ET.SubElement(self.parent, "stringConstant")
            elem.text = txt
            self.tknzr.advance()
            # construct a String object
            self.vm_writer.write_push(SegmentType.CONSTANT, len(txt))
            self.vm_writer.write_call("String.new", 1)
            for c in txt:
                self.vm_writer.write_push(SegmentType.CONSTANT, ord(c))
                self.vm_writer.write_call("String.appendChar", 2)
        elif self.tknzr.token_type() == TokenType.KEYWORD:
            # keyword
            keyword = self.__add_keyword({"true","false","null","this"})
            if keyword == "true":
                self.vm_writer.write_push(SegmentType.CONSTANT, 0)
                self.vm_writer.write_arithmetic("not")
            elif keyword == "null" or keyword == "false":
                self.vm_writer.write_push(SegmentType.CONSTANT, 0)
            else:  # this
                self.vm_writer.write_push(SegmentType.POINTER, 0)
        elif self.tknzr.token_type() == TokenType.IDENTIFIER:
            # varName | varName '[' expression ']' | subroutineCall
            if self.tknzr.token_lookahead() == '[':
                # varName '[' expression ']'
                var_name = self.__add_identifier_var()
                var_prop = self.__look_up_in_symbol_table(var_name)
                self.__add_symbol({'['})
                self.compile_expression()
                self.__add_symbol({']'})
                # put the value of varName at the stack's top
                self.vm_writer.write_push(VAR_KIND_TO_SEG[var_prop.kind], var_prop.index)
                # calc (varName + expression)
                self.vm_writer.write_arithmetic("add")
                # that = varName + expression
                self.vm_writer.write_pop(SegmentType.POINTER, 1)  # that = varName + expression
                # put *(that+0) at the stack's top
                self.vm_writer.write_push(SegmentType.THAT, 0)
            elif self.tknzr.token_lookahead() in {'(', '.'}:
                # subroutineCall
                self.__compile_subroutine_call()
            else:
                # varName
                var_name = self.__add_identifier_var()
                var_prop = self.__look_up_in_symbol_table(var_name)
                self.vm_writer.write_push(VAR_KIND_TO_SEG[var_prop.kind], var_prop.index)
        else:
            # '(' expression ')' | (unaryOp term) 
            if self.tknzr.symbol() == '(':
                # '(' expression ')'
                self.__add_symbol({'('})
                self.compile_expression()
                self.__add_symbol({')'})
            else:
                # (unaryOp term) 
                uop = self.__add_symbol({'-','~'})
                self.compile_term()
                # output op
                self.vm_writer.write_arithmetic(VMWriter.al_uop2cmd[uop])

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
            xml_file_path = self.jack_file_path.with_suffix(".xml")
            pretty_print(self.root)
            ET.ElementTree(self.root).write(xml_file_path)
            print(f"XML file written to [{xml_file_path}]")

    def close(self, write_xml=False):
        '''Finishes compilation.'''
        if write_xml:
            self.write_to_xml()
        self.vm_writer.close()
    
    def __compile_subroutine_call(self):
        # subroutineCall
        # grammer: (className|varName) '.' subroutineName '(' expressionList ')' |
        #                                  subroutineName '(' expressionList ')'
        if self.tknzr.token_lookahead() == '.':
            # expecting (className|varName) '.'
            try:
                # varName.xxx (a method)
                var_name = self.__add_identifier_var()
                var_prop = self.__look_up_in_symbol_table(var_name)
                self.vm_writer.write_push(VAR_KIND_TO_SEG[var_prop.kind], var_prop.index)  # push varName
                has_this = True
                cls_name = self.__look_up_in_symbol_table(var_name).vtype
            except:
                # className.xxx (a function)
                has_this = False
                cls_name = self.__add_identifier_cls()
            self.__add_symbol({'.'})
            cls_name += '.'
        else:  # subroutineName(...) (a method)
            cls_name = self.cls_name + '.'  # name of this class
            self.vm_writer.write_push(SegmentType.POINTER, 0)  # push this
            has_this = True
        # expecting subroutineName '(' expressionList ')'
        sub_name = self.__add_identifier_sub()
        func_name = cls_name + sub_name
        self.__add_symbol({'('})
        n_args = self.compile_expression_list()
        self.__add_symbol({')'})
        # write "call f n"
        self.vm_writer.write_call(func_name, n_args + (1 if has_this else 0))
    
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

    def __look_up_in_symbol_table(self, name):
        if self.tbl_subroutine.contains(name):
            return self.tbl_subroutine.get(name)
        elif self.tbl_class.contains(name):
            return self.tbl_class.get(name)
        else:
            raise NameError(f"Undefined Variable: {name}")

    def __add_identifier(self, usage, lookup, category, advance):
        # read the identifier
        identifier = self.__get_identifier()
        # symbol table look up
        index = -1
        if lookup:
            var_prop = self.__look_up_in_symbol_table(identifier)
            category, index = var_prop.kind.name, var_prop.index
        # add identifier to the element tree
        elem = ET.SubElement(self.parent, "identifier")
        # name
        sub_elem = ET.SubElement(elem, "name")
        sub_elem.text = identifier
        # category
        sub_elem = ET.SubElement(elem, "category")
        sub_elem.text = category
        # index
        if index >= 0:
            sub_elem = ET.SubElement(elem, "index")
            sub_elem.text = str(index)
        # usage
        sub_elem = ET.SubElement(elem, "usage")
        sub_elem.text = usage.name
        if advance:
            self.tknzr.advance()
        return identifier

    def __add_identifier_var(self, usage=UsageType.USED, advance=True):
        return self.__add_identifier(usage, True, "", advance)

    def __add_identifier_cls(self, usage=UsageType.USED, advance=True):
        return self.__add_identifier(usage, False, "CLASS", advance)
    
    def __add_identifier_sub(self, usage=UsageType.USED, advance=True):
        return self.__add_identifier(usage, False, "SUBROUTINE", advance)

    def __add_type(self, advance=True):
        # expecting 'int' or 'char' or 'boolean' or className
        try:  # 'int' | 'char' | 'boolean'
            t = self.__add_keyword({"int", "char", "boolean"}, advance)
        except:  # className
            t = self.__add_identifier_cls(advance=advance)
        return t
