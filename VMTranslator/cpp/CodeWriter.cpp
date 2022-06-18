// implementation details of the CodeWriter

#include "CodeWriter.hpp"
#include "asm_ops.hpp"

#include <sstream>
#include <cassert>

// ============================================================ //

std::string compare_top2(const std::string& j_cond) 
{
	// compare (and pop) top 2 elements in the stack
	// and push the comparison result
	std::stringstream code, code_if_true, code_if_false;
	code_if_true << ASM::DNCHG::star_ptrm1("SP") << "M=-1\n";
	code_if_false << ASM::DNCHG::star_ptrm1("SP") << "M=0\n";
	code << ASM::DCHG::stack_pop()  // D = value popped
		// D = *(SP-1) - D 
		<< ASM::DNCHG::star_ptrm1("SP")
		<< "D=M-D\n"
		<< ASM::DNCHG::if_else(j_cond, code_if_true.str(), code_if_false.str());
	return code.str();
}

// ============================================================ //

void CodeWriter::write_arithmetic(const std::string& cmd)
{
	std::stringstream code;
	code << "// " << cmd << std::endl;
	if (cmd == "add") {
		code << ASM::DCHG::stack_pop()  // D = value popped
			<< ASM::DNCHG::star_ptrm1("SP") 
			<< "M=D+M\n";
	}
	else if (cmd == "sub") {
		code << ASM::DCHG::stack_pop()  // D = value popped
			<< ASM::DNCHG::star_ptrm1("SP") 
			<< "M=M-D\n";
	}
	else if (cmd == "neg") {
		code << ASM::DNCHG::star_ptrm1("SP") 
			<< "M=-M\n";
	}
	else if (cmd == "eq") {
		code << compare_top2("JEQ");
	}
	else if (cmd == "gt") {
		code << compare_top2("JGT");
	}
	else if (cmd == "lt") {
		code << compare_top2("JLT");
	}
	else if (cmd == "and") {
		code << ASM::DCHG::stack_pop()  // D = value popped
			<< ASM::DNCHG::star_ptrm1("SP") 
			<< "M=D&M\n";
	}
	else if (cmd == "or") {
		code << ASM::DCHG::stack_pop()  // D = value popped
			<< ASM::DNCHG::star_ptrm1("SP") 
			<< "M=D|M\n";
	}
	else if (cmd == "not") {
		code << ASM::DNCHG::star_ptrm1("SP") 
			<< "M=!M\n";
	}
	else {
		auto error_msg = std::format("Invalid arithmetic command: [{}]", cmd);
		throw std::invalid_argument(error_msg);
	}
	m_f_asm << code.str();
}

// ============================================================ //

void CodeWriter::write_push_pop(CmdType cmd_t, const std::string& seg, int idx)
{
	std::stringstream code;
	switch (cmd_t)
	{
	case CmdType::C_PUSH:
		code << "// push " << seg << " " << idx << std::endl;
		if (seg == "local") {
			code << ASM::DCHG::stack_push("LCL", idx);
		}
		else if (seg == "argument") {
			code << ASM::DCHG::stack_push("ARG", idx);
		}
		else if (seg == "this") {
			code << ASM::DCHG::stack_push("THIS", idx);
		}
		else if (seg == "that") {
			code << ASM::DCHG::stack_push("THAT", idx);
		}
		else if (seg == "static") {
			code << ASM::DCHG::stack_push_static(m_f_name, idx);
		}
		else if (seg == "constant") {
			code << ASM::DCHG::stack_push(idx);
		}
		else if (seg == "temp") {
			code << ASM::DCHG::assign("R13", 5)
				<< ASM::DCHG::stack_push("R13", idx);
		}
		else if (seg == "pointer") {
			code << ASM::DCHG::stack_push_pointer(idx);
		}
		else {
			auto error_msg = std::format("Invalid segment type: [{}].", seg);
			throw std::invalid_argument(error_msg);
		}
		break;
	case CmdType::C_POP:
		code << "// pop" << seg << " " << idx << std::endl;
		if (seg == "local") {
			code << ASM::DCHG::stack_pop("LCL", idx);
		}
		else if (seg == "argument") {
			code << ASM::DCHG::stack_pop("ARG", idx);
		}
		else if (seg == "this") {
			code << ASM::DCHG::stack_pop("THIS", idx);
		}
		else if (seg == "that") {
			code << ASM::DCHG::stack_pop("THAT", idx);
		}
		else if (seg == "static") {
			code << ASM::DCHG::stack_pop_static(m_f_name, idx);
		}
		else if (seg == "temp") {
			code << ASM::DCHG::assign("R13", 5)
				<< ASM::DCHG::stack_pop("R13", idx);
		}
		else if (seg == "pointer") {
			code << ASM::DCHG::stack_pop_pointer(idx);
		}
		else {
			auto error_msg = std::format("Invalid segment type: [{}].", seg);
			throw std::invalid_argument(error_msg);
		}
		break;
	default:
		throw std::invalid_argument("Invalid command type.");
		break;
	}
	m_f_asm << code.str();
}

// ============================================================ //
