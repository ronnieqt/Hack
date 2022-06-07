// implementation details of asm ops

#include "asm_ops.hpp"

#include <sstream>
#include <format>

// ============================================================ //

std::string ASM::DNCHG::ptr_pp(const std::string& ptr)
{
	std::stringstream code;
	code << "@" << ptr << std::endl
		<< "M=M+1\n";
	return code.str();
}

std::string ASM::DNCHG::ptr_mm(const std::string& ptr)
{
	std::stringstream code;
	code << "@" << ptr << std::endl
		<< "M=M-1\n";
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DNCHG::star()
{
	return "A=D\n";
}

std::string ASM::DNCHG::star_ptr(const std::string& ptr)
{
	// @ptr
	// A=M  // after this, M = RAM[A], D remains untouched
	std::stringstream code;
	code << "@" << ptr << std::endl
		<< "A=M\n";
	return code.str();
}

std::string ASM::DNCHG::star_ptrm1(const std::string& ptr)
{
	std::stringstream code;
	code << "@" << ptr << std::endl
		<< "A=M-1\n";
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DNCHG::stack_push()
{
	std::stringstream code;
	// *SP = D
	code << star_ptr("SP") << "M=D\n";
	// SP++
	code << ptr_pp("SP");
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DNCHG::assign(const std::string& var)
{
	// assign the current value in the D register to the variable 'var'
	// @var
	// M=D
	std::stringstream code;
	code << "@" << var << std::endl << "M=D\n";
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DNCHG::if_else(
	const std::string& j_cond,
	const std::string& t_part,
	const std::string& f_part
) {
	static int count = 0;
	std::stringstream code;
	// if (...)
	code << "@IF_TRUE_" << count << std::endl;
	code << "D;" << j_cond << std::endl;
	// actions (if false)
	code << f_part;
	code << "@CONTINUE_" << count << std::endl;
	code << "0;JMP\n";
	// actions (if true)
	code << "(IF_TRUE_" << count << ")\n";
	code << t_part;
	code << "(CONTINUE_" << count << ")\n";
	// increase the counter
	count++;
	return code.str();
}

// ============================================================ //

std::string ASM::DCHG::ptr_pi(const std::string& ptr, int i)
{
	std::stringstream code;
	code << "@" << i << std::endl
		<< "D=A\n"
		<< "@" << ptr << std::endl
		<< "D=D+M\n";
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DCHG::stack_push(int val)
{
	std::stringstream code;
	// D = val
	code << "@" << val << std::endl;
	code << "D=A\n";
	// push D into stack
	code << DNCHG::stack_push();
	return code.str();
}

std::string ASM::DCHG::stack_push(const std::string& seg, int i)
{
	std::stringstream code;
	// D = *(segment_pointer + i)
	code << DCHG::ptr_pi(seg, i)
		<< DNCHG::star()
		<< "D=M\n"
		<< DNCHG::stack_push();
	return code.str();
}

std::string ASM::DCHG::stack_push_static(const std::string& f_name, int i)
{
	std::stringstream code;
	code << "@" << std::format("{}.{}\n", f_name, i)
		<< "D=M\n"
		<< DNCHG::stack_push();
	return code.str();
}

std::string ASM::DCHG::stack_push_pointer(int i)
{
	std::stringstream code;
	code << "@" << (i == 0 ? "THIS" : "THAT") << std::endl
		<< "D=M\n"
		<< DNCHG::star_ptr("SP")
		<< "M=D\n"
		<< DNCHG::ptr_pp("SP");
	return code.str();
}

std::string ASM::DCHG::stack_pop()
{
	std::stringstream code;
	// SP--
	code << DNCHG::ptr_mm("SP");
	// D = *SP
	code << DNCHG::star_ptr("SP") << "D=M\n";
	return code.str();
}

std::string ASM::DCHG::stack_pop(const std::string& seg, int i)
{
	std::stringstream code;
	// R13 = segmentPointer + i, SP--, *R13 = *SP
	code << ASM::DCHG::ptr_pi(seg, i) << DNCHG::assign("R13")
		<< ASM::DNCHG::ptr_mm("SP")
		<< ASM::DNCHG::star_ptr("SP") << "D=M\n"
		<< ASM::DNCHG::star_ptr("R13") << "M=D\n";
	return code.str();
}

std::string ASM::DCHG::stack_pop_static(const std::string& f_name, int i)
{
	std::stringstream code;
	code << stack_pop()
		<< "@" << std::format("{}.{}\n", f_name, i)
		<< "M=D\n";
	return code.str();
}

std::string ASM::DCHG::stack_pop_pointer(int i)
{
	std::stringstream code;
	code << DNCHG::ptr_mm("SP")
		<< DNCHG::star_ptr("SP")
		<< "D=M\n"
		<< "@" << (i == 0 ? "THIS" : "THAT") << std::endl
		<< "M=D\n";
	return code.str();
}

// ------------------------------------------------------------ //

std::string ASM::DCHG::assign(const std::string& var, int val)
{
	std::stringstream code;
	code << "@" << val << std::endl << "D=A\n"
		<< DNCHG::assign(var);
	return code.str();
}

// ============================================================ //
