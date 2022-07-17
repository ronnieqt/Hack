from enum import Enum, unique

@unique
class TokenType(Enum):
    UNKNOWN = -1
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4

@unique
class VarKind(Enum):
    NONE = -1
    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3

@unique
class UsageType(Enum):
    USED = 0
    DECLARED = 1

@unique
class SegmentType(Enum):
    CONSTANT = 0
    ARGUMENT = 1
    LOCAL = 2
    STATIC = 3
    THIS = 4
    THAT = 5
    POINTER = 6
    TEMP = 7
