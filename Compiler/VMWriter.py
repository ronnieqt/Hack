"""
This module features a set of simple routines for
    writing VM commands into the output file.
"""

# %% import libs

from MyTypes import SegmentType

from pathlib import Path

# %% class definition

class VMWriter:

    def __init__(self, vm_file_path: Path) -> None:
        """Creates a new output .vm file/stream, and prepares it for writing."""
        self.f_vm = open(vm_file_path, "w")

    def write_push(self, segment: SegmentType, index: int) -> None:
        """Writes a VM push command."""
        self.f_vm.write(f"push {segment.name.lower()} {index}")

    def write_pop(self, segment: SegmentType, index: int) -> None:
        """Writes a VM pop command."""
        assert segment != SegmentType.CONSTANT, "Cannot pop a constant!"
        self.f_vm.write(f"pop {segment.name.lower()} {index}")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic-logical command."""
        assert command in {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        self.f_vm.write(command)

    def write_label(self, label: str) -> None:
        """Writes a VM label command."""
        self.f_vm.write(f"label {label}")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command."""
        self.f_vm.write(f"goto {label}")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command."""
        self.f_vm.write(f"if-goto {label}")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call commands."""
        self.f_vm.write(f"call {name} {n_args}")

    def write_function(self, name: str, n_vars: int) -> None:
        """Writes a VM function command."""
        self.f_vm.write(f"function {name} {n_vars}")

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.f_vm.write("return")

    def close(self) -> None:
        """Closes the output file/stream."""
        print(f"VM file written to [{self.f_vm}]")
        self.f_vm.close()
