# %% Import Libs

from pathlib import Path
from collections import defaultdict

from MyTypes import CmdType

import dnchg, dchg

# %% utils

def compare_top2(j_cond):
    code_if_true = dnchg.star_ptrm1("SP") + "M=-1\n"
    code_if_false = dnchg.star_ptrm1("SP") + "M=0\n"
    return (
        dchg.stack_pop() +
        dnchg.star_ptrm1("SP") +
        "D=M-D\n" +
        dnchg.if_else(j_cond, code_if_true, code_if_false)
    )

# %% Class Def

class CodeWriter:

    def __init__(self, asm_file_path: Path):
        self.f_asm = open(asm_file_path, 'w')
        self.vm_f_name = asm_file_path.stem
        self.curr_func_name = ""
        self.n_func_calls = defaultdict(lambda: 0)
        self.write_bootstrap()

    def set_file_name(self, file_name: str):
        self.vm_f_name = file_name
        self.curr_func_name = ""

    def write_bootstrap(self):
        code = "// Bootstrap\n" + dchg.assign_val2var("SP", 256)
        self.f_asm.write(code)
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, cmd: str):
        code = f"// {cmd}\n"
        if cmd == "add":
            code += dchg.stack_pop() + dnchg.star_ptrm1("SP") + "M=D+M\n"
        elif cmd == "sub":
            code += dchg.stack_pop() + dnchg.star_ptrm1("SP") + "M=M-D\n"
        elif cmd == "neg":
            code += dnchg.star_ptrm1("SP") + "M=-M\n"
        elif cmd == "eq":
            code += compare_top2("JEQ")
        elif cmd == "gt":
            code += compare_top2("JGT")
        elif cmd == "lt":
            code += compare_top2("JLT")
        elif cmd == "and":
            code += dchg.stack_pop() + dnchg.star_ptrm1("SP") + "M=D&M\n"
        elif cmd == "or":
            code += dchg.stack_pop() + dnchg.star_ptrm1("SP") + "M=D|M\n"
        elif cmd == "not":
            code += dnchg.star_ptrm1("SP") + "M=!M\n"
        else:
            raise Exception(f"Invalid arithmetic command: [{cmd}]")
        self.f_asm.write(code)

    def write_push_pop(self, cmd_t: CmdType, seg: str, idx: int):
        code = ""
        if cmd_t == CmdType.C_PUSH:
            code += f"// push {seg} {idx}\n"
            if seg == "local":
                code += dchg.stack_push_seg("LCL", idx)
            elif seg == "argument":
                code += dchg.stack_push_seg("ARG", idx)
            elif seg == "this":
                code += dchg.stack_push_seg("THIS", idx)
            elif seg == "that":
                code += dchg.stack_push_seg("THAT", idx)
            elif seg == "static":
                code += dchg.stack_push_static(self.vm_f_name, idx)
            elif seg == "constant":
                code += dchg.stack_push_val(idx)
            elif seg == "temp":
                code += dchg.assign_val2var("R13", 5) + dchg.stack_push_seg("R13", idx)
            elif seg == "pointer":
                code += dchg.stack_push_pointer(idx)
            else:
                raise Exception(f"Invalid segment type: [{seg}]")
            pass
        elif cmd_t == CmdType.C_POP:
            code += f"// pop {seg} {idx}\n"
            if seg == "local":
                code += dchg.stack_pop_seg("LCL", idx)
            elif seg == "argument":
                code += dchg.stack_pop_seg("ARG", idx)
            elif seg == "this":
                code += dchg.stack_pop_seg("THIS", idx)
            elif seg == "that":
                code += dchg.stack_pop_seg("THAT", idx)
            elif seg == "static":
                code += dchg.stack_pop_static(self.vm_f_name, idx)
            elif seg == "temp":
                code += dchg.assign_val2var("R13", 5) + dchg.stack_pop_seg("R13", idx)
            elif seg == "pointer":
                code += dchg.stack_pop_pointer(idx)
            else:
                raise Exception(f"Invalid segment type: [{seg}]")
        else:
            raise Exception(f"Invalid command type: [{cmd_t.name}]")
        self.f_asm.write(code)

    def write_label(self, label: str):
        prefix = self.get_label_prefix()
        code = f"// label {label}\n" + f"({prefix}{label})\n"
        self.f_asm.write(code)

    def write_goto(self, label: str):
        prefix = self.get_label_prefix()
        code = f"// goto {label}\n" + f"@{prefix}{label}\n" + "0;JMP\n"
        self.f_asm.write(code)

    def write_if(self, label: str):
        prefix = self.get_label_prefix()
        code = f"// if-goto {label}\n" \
            + dchg.stack_pop() \
            + f"@{prefix}{label}\n" \
            + "D;JNE\n"  # true: -1; false: 0
        self.f_asm.write(code)

    def write_function(self, func_name: str, n_vars: int):
        self.curr_func_name = func_name
        code = f"// function {func_name} {n_vars}\n"
        # injects a function entry label
        code += f"({func_name})\n"
        # initialize n_vars local variables to 0
        for i in range(n_vars):
            code += dchg.stack_push_val(0) # + dchg.stack_pop_seg("LCL", i)
        self.f_asm.write(code)
    
    def write_return(self):
        code = (
            "// return\n" 
            # R14 (frame) = LCL
            + dchg.assign_var2var("LCL", "R14")
            # R15 (retAddr) = *(frame - 5)
            + dchg.var_mi("R14", 5) + dnchg.star() + "D=M\n" + dnchg.assign_d2var("R15")
            # *ARG = pop()
            + dchg.stack_pop() + dnchg.star_ptr("ARG") + "M=D\n" 
            # SP = ARG + 1
            + dchg.var_pi("ARG", 1) + dnchg.assign_d2var("SP") 
            # THAT = *(frame - 1)
            + dchg.var_mi("R14", 1) + dnchg.star() + "D=M\n" + dnchg.assign_d2var("THAT")
            # THIS = *(frame - 2)
            + dchg.var_mi("R14", 2) + dnchg.star() + "D=M\n" + dnchg.assign_d2var("THIS")
            # ARG = *(frame - 3)
            + dchg.var_mi("R14", 3) + dnchg.star() + "D=M\n" + dnchg.assign_d2var("ARG")
            # LCL = *(frame - 4)
            + dchg.var_mi("R14", 4) + dnchg.star() + "D=M\n" + dnchg.assign_d2var("LCL")
            # goto retAddr
            + dnchg.star_ptr("R15") + "0;JMP\n"
        )
        self.f_asm.write(code)
    
    def write_call(self, func_name: str, n_args: int):
        return_address = f"{func_name}$ret.{self.n_func_calls[func_name]}"
        self.n_func_calls[func_name] += 1
        code = (
            f"// call {func_name} {n_args}\n"
            # push returnAddress
            + dchg.stack_push_val(return_address)
            # push LCL
            + dchg.stack_push_var("LCL")
            # push ARG
            + dchg.stack_push_var("ARG")
            # push THIS 
            + dchg.stack_push_var("THIS")
            # push TAHT
            + dchg.stack_push_var("THAT")
            # ARG = SP - 5 - nArgs
            + dchg.var_mi("SP", 5+n_args) + dnchg.assign_d2var("ARG")
            # LCL = SP
            + dchg.assign_var2var("SP", "LCL")
            # goto f
            + f"@{func_name}\n" + "0;JMP\n"
            # (returnAddress)
            + f"({return_address})\n"
        )
        self.f_asm.write(code)

    def close(self):
        # self.f_asm.write("(END)\n@END\n0;JMP\n")
        self.f_asm.close()

    def get_label_prefix(self):
        return (self.curr_func_name + "$") if self.curr_func_name else ""
