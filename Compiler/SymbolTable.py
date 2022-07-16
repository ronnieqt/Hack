"""
This module provides services for building, populating, and
    using symbol tables that keep track of the symbol properties
    name, type, kind, and a running index for each kind.
"""

# %% import libs

from MyTypes import VarKind
from collections import defaultdict

# %% Variable Properties

class VarProp:

    def __init__(self, vtype: str, kind: VarKind, index: int) -> None:
        """Variable Properties
        type: int, char, boolean, class name
        kind: field, static, local, argument
        index: 0, 1, 2, ...
        """
        self.vtype = vtype
        self.kind = kind
        self.index = index

# %% class definition

class SymbolTable:
    """SymbolTable: {name, type, kind, index}."""

    def __init__(self) -> None:
        """Creates a new symbol table."""
        self.reset()

    def reset(self) -> None:
        """Empties the symbol table, and resets the 4 indexes to 0.
        Note: should be called when starting to compile a subroutine declaration.
        """
        self.data = dict()                     # {name: var_prop}
        self.counter = defaultdict(lambda: 0)  # {var_kind: n_in_the_table}

    def define(self, name: str, vtype: str, kind: VarKind) -> None:
        """Defines a new variable of the given name, type, and kind."""
        # assigns to the new var the index of that kind
        self.data[name] = VarProp(vtype, kind, self.counter[kind])
        # adds 1 to the index
        self.counter[kind] += 1

    def var_count(self, kind: VarKind) -> int:
        """Returns the number of variables of the given kind already defined in the table."""
        return self.counter[kind]

    def kind_of(self, name: str) -> VarKind:
        """Returns the kind of the named identifier."""
        if name in self.data:
            return self.data[name].kind
        else:  # if the identifier is not found, returns NONE
            return VarKind.NONE

    def type_of(self, name: str) -> str:
        """Returns the type of the named variable."""
        return self.data[name].vtype

    def index_of(self, name: str) -> int:
        """Returns the index of the named variable."""
        return self.data[name].index
    
    def contains(self, name: str) -> bool:
        """Checks whether the symbol contains the given name or not."""
        return name in self.data
