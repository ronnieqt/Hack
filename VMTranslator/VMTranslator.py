# %% Import Libs

import argparse

from pathlib import Path

from Parser import Parser
from MyTypes import CmdType
from CodeWriter import CodeWriter

# %% vm file processing

def process_vm_file(vm_file_path: Path, writer: CodeWriter):

    print(f"Parsing [{vm_file_path}]... ", end="")

    parser = Parser(vm_file_path)
    writer.set_file_name(vm_file_path.name)

    while parser.has_more_lines():
        parser.advance()
        if not parser.is_curr_cmd_valid():
            continue
        cmd_t = parser.command_type()
        if cmd_t == CmdType.C_ARITHMETIC:
            writer.write_arithmetic(parser.arg1())
        elif (cmd_t == CmdType.C_PUSH) or (cmd_t == CmdType.C_POP):
            writer.write_push_pop(cmd_t, parser.arg1(), parser.arg2())
        elif cmd_t == CmdType.C_LABEL:
            writer.write_label(parser.arg1())
        elif cmd_t == CmdType.C_GOTO:
            writer.write_goto(parser.arg1())
        elif cmd_t == CmdType.C_IF:
            writer.write_if(parser.arg1())
        elif cmd_t == CmdType.C_FUNCTION:
            writer.write_function(parser.arg1(), parser.arg2())
        elif cmd_t == CmdType.C_RETURN:
            writer.write_return()
        elif cmd_t == CmdType.C_CALL:
            writer.write_call(parser.arg1(), parser.arg2())
        else:
            raise Exception(f"Unrecognized command type: [{cmd_t.name}]")

    parser.close()

    print("done...")

# %% main

def _main():

    # argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    options = parser.parse_args()

    # path processing
    input_path = Path(options.file)
    if input_path.is_dir():
        vm_files = input_path.glob("*.vm")
        asm_file_path = (input_path/input_path.name).with_suffix(".asm")
    else:
        vm_files = [input_path]
        asm_file_path = input_path.with_suffix(".asm")

    writer = CodeWriter(asm_file_path)

    for vm_file in vm_files:
        process_vm_file(vm_file, writer)

    writer.close()

    print(f"File written to: {asm_file_path}")

# %% run main

if __name__ == "__main__":
    _main()
