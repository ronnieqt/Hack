from enum import Enum, unique

@unique
class TokenType(Enum):
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4
    UNKNOWN = 5

@unique
class VarKind(Enum):
    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3
    NONE = 4

@unique
class UsageType(Enum):
    USED = 0
    DECLARED = 1
