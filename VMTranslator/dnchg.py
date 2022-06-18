# %% variable ops

def var_pp(var):
    return (
        f"@{var}\n" +
        "M=M+1\n"
    )

def var_mm(var):
    return (
        f"@{var}\n" +
        "M=M-1\n"
    )

# %% pointer ops

def star():
    return "A=D\n"

def star_ptr(ptr):
    return (
        f"@{ptr}\n" +
        "A=M\n"
    )

def star_ptrm1(ptr):
    return (
        f"@{ptr}\n" +
        "A=M-1\n"
    )

# %% stack ops

def stack_push():
    return (
        star_ptr("SP") +
        "M=D\n" +
        var_pp("SP")
    )

# %% utils

def assign_d2var(var):
    return (
        f"@{var}\n" +
        "M=D\n"
    )

def if_else(j_cond, t_part, f_part):
    if not hasattr(if_else, "count"):
        if_else.count = 0
    if_else.count += 1  # add attribution to a function
    return (
        f"@__IF_TRUE_{if_else.count}\n" +
        f"D;{j_cond}\n" +
        f_part +
        f"@__CONTINUE_{if_else.count}\n" +
        "0;JMP\n" +
        f"(__IF_TRUE_{if_else.count})\n" +
        t_part +
        f"(__CONTINUE_{if_else.count})\n"
    )
