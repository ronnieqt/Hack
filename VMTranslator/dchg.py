# %% Import Libs

import dnchg

# %% variable ops (DCHG)

def var_p1(var):
    return (
        f"@{var}\n" +
        "D=M+1\n"
    )

def var_pi(var, i):
    return (
        f"@{i}\n" +
        "D=A\n" +
        f"@{var}\n" +
        "D=D+M\n"
    ) if (i != 1) else var_p1(var)

def var_m1(var):
    return (
        f"@{var}\n" +
        "D=M-1\n"
    )

def var_mi(var, i):
    return (
        f"@{i}\n" +
        "D=A\n" +
        f"@{var}\n" +
        "D=M-D\n"
    ) if (i != 1) else var_m1(var)

# %% stack ops (DCHG)

def stack_push_val(val):
    return (
        f"@{val}\n" +
        "D=A\n" +
        dnchg.stack_push()
    )

def stack_push_var(var):
    return (
        f"@{var}\n" +
        "D=M\n" +
        dnchg.stack_push()
    )

def stack_push_seg(seg, i):
    return (
        var_pi(seg, i) +
        dnchg.star() +
        "D=M\n" +
        dnchg.stack_push()
    )

def stack_push_static(f_name, i):
    return (
        f"@{f_name}.{i}\n" +
        "D=M\n" +
        dnchg.stack_push()
    )

def stack_push_pointer(i):
    return (
        f"@{'THIS' if (i == 0) else 'THAT'}\n" +
        "D=M\n" +
        dnchg.star_ptr("SP") +
        "M=D\n" +
        dnchg.var_pp("SP")
    )

def stack_pop():
    return (
        dnchg.var_mm("SP") +
        dnchg.star_ptr("SP") +
        "D=M\n"
    )

def stack_pop_seg(seg, i):
    return (
        var_pi(seg, i) + dnchg.assign_d2var("R13") +
        dnchg.var_mm("SP") +
        dnchg.star_ptr("SP") + "D=M\n" +
        dnchg.star_ptr("R13") + "M=D\n"
    )

def stack_pop_static(f_name, i):
    return (
        stack_pop() +
        f"@{f_name}.{i}\n" +
        "M=D\n"
    )

def stack_pop_pointer(i):
    return (
        dnchg.var_mm("SP") +
        dnchg.star_ptr("SP") +
        "D=M\n" +
        f"@{'THIS' if (i == 0) else 'THAT'}\n" +
        "M=D\n"
    )

# %% utils (DCHG)

def assign_val2var(var, val):
    return (
        f"@{val}\n" +
        "D=A\n" +
        dnchg.assign_d2var(var)
    )

def assign_var2var(var_from, var_to):
    return (
        f"@{var_from}\n" +
        "D=M\n" +
        dnchg.assign_d2var(var_to)
    )
