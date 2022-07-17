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
        pass

    def write_push(self, segment: SegmentType, index: int) -> None:
        """Writes a VM push command."""
        pass

    def write_pop(self, segment: SegmentType, index: int) -> None:
        """Writes a VM pop command."""
        assert segment != SegmentType.CONSTANT, "Cannot pop a constant!"
        pass

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic-logical command."""
        assert command in {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        pass

    def write_label(self, label: str) -> None:
        """Writes a VM label command."""
        pass

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command."""
        pass

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command."""
        pass

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call commands."""
        pass

    def write_function(self, name: str, n_vars: int) -> None:
        """Writes a VM function command."""
        pass

    def write_return(self) -> None:
        """Writes a VM return command."""
        pass

    def close(self) -> None:
        """Closes the output file/stream."""
        self.f_vm.close()
