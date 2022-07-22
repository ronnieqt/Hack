"""
Compile .jack file into binary codes.
"""

# %% import libs

from pathlib import Path
from argparse import ArgumentParser

import subprocess

# %% main program

def _main():
    # CLI args
    parser = ArgumentParser()
    parser.add_argument("jack_files", help="Jack file(s) path.", type=str)
    args = parser.parse_args()
    # software paths
    p_hack = Path(__file__).parent
    compiler = p_hack / "Compiler/JackCompiler.py"
    vm_translator = p_hack / "VMTranslator/VMTranslator.py"
    assembler = p_hack / "Assembler/x64/Release/Assembler.exe"
    # file paths
    f_jack = Path(args.jack_files)
    if f_jack.is_dir():
        f_vm = f_jack
        f_asm = f_jack / f"{f_jack.name}.asm"
    else:
        f_vm = f_jack.with_suffix(".vm")
        f_asm = f_jack.with_suffix(".asm")
    # software calls
    subprocess.run(["python", compiler, f_jack], check=True)
    subprocess.run(["python", vm_translator, f_vm], check=True)
    subprocess.run([assembler, f_asm], check=True)

if __name__ == "__main__":
    _main()
