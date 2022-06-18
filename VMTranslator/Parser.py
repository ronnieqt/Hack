# %% Import Libs

import re

from MyTypes import CmdType

# %% Helper Functions

def format_input(input: str):
    # remove comments
    input = re.sub(r"//.*$", "", input)
    # remove leading and trailing whitespaces
    input = input.strip()
    return input

# %% Class Definition

class Parser:
    
    # static vars
    al_cmds = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}

    def __init__(self, vm_file_path):
        self.f_vm = open(vm_file_path, 'r')
        self._has_more_lines = True
        self.curr_cmd = ""

    def has_more_lines(self):
        return self._has_more_lines

    def advance(self):
        while self.has_more_lines():
            line = self.f_vm.readline()
            if line == '':  # EOF
                self.curr_cmd = ""
                self._has_more_lines = False
                break
            self.curr_cmd = format_input(line)
            if self.is_curr_cmd_valid():
                break

    def command_type(self):
        if self.curr_cmd in self.al_cmds:
            return CmdType.C_ARITHMETIC
        elif self.curr_cmd.startswith("push"):
            return CmdType.C_PUSH
        elif self.curr_cmd.startswith("pop"):
            return CmdType.C_POP
        elif self.curr_cmd.startswith("label"):
            return CmdType.C_LABEL
        elif self.curr_cmd.startswith("goto"):
            return CmdType.C_GOTO
        elif self.curr_cmd.startswith("if-goto"):
            return CmdType.C_IF
        elif self.curr_cmd.startswith("function"):
            return CmdType.C_FUNCTION
        elif self.curr_cmd == "return":
            return CmdType.C_RETURN
        elif self.curr_cmd.startswith("call"):
            return CmdType.C_CALL
        else:
            return CmdType.C_INVALID

    def arg1(self):
        cmd_t = self.command_type()
        assert cmd_t != CmdType.C_RETURN
        if cmd_t == CmdType.C_ARITHMETIC:
            return self.curr_cmd
        else:
            return self.curr_cmd.split(' ')[1]

    def arg2(self):
        cmd_t = self.command_type()
        assert cmd_t == CmdType.C_PUSH \
            or cmd_t == CmdType.C_POP \
            or cmd_t == CmdType.C_FUNCTION \
            or cmd_t == CmdType.C_CALL
        return int(self.curr_cmd.split(' ')[2])
    
    def close(self):
        self.f_vm.close()

    def is_curr_cmd_valid(self):
        is_empty = self.curr_cmd == ''
        is_comment = self.curr_cmd.startswith("//")
        return (not is_empty) and (not is_comment)

# %% Testing

def _main():
    print(format_input("   abc // def  "))
    parser = Parser("./tests/MemoryAccess/BasicTest/BasicTest.vm")
    print(parser._has_more_lines)

if __name__ == "__main__":
    _main()
