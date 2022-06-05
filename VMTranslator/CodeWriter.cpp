// implementation details of the CodeWriter

#include "CodeWriter.hpp"
#include "asm_ops.hpp"

#include <sstream>

// ============================================================ //

std::string assign(const std::string& name)
{
	std::stringstream code;
	code << "@" << name << std::endl << "M=D\n";
	return code.str();
}

std::string assign(const std::string& name, int val)
{
	std::stringstream code;
	code << "@" << val << std::endl << "D=A\n"
		<< assign(name);
	return code.str();
}

std::string assign_static(const std::string& f_name, int val)
{
	static int count = 0;
	auto code = assign(std::format("{}.{}", f_name, count), val);
	count++;
	return code;
}

// ============================================================ //

std::string stack_push(const std::string& seg, int i)
{
	std::stringstream code;
	// D = *(segment_pointer + i)
	code << ASM::DCHG::ptr_pi(seg, i)
		<< ASM::DNCHG::star()
		<< "D=M\n"
		<< ASM::DNCHG::stack_push();
	return code.str();
}

// ============================================================ //

std::string stack_pop(const std::string& seg, int i)
{
	std::stringstream code;
	// addr = segmentPointer + i, SP--, *addr = *SP
	code << ASM::DCHG::ptr_pi(seg, i) << assign("addr")
		<< ASM::DNCHG::ptr_mm("SP")
		<< ASM::DNCHG::star_ptr("SP") << "D=M\n"
		<< ASM::DNCHG::star_ptr("addr") << "M=D\n";
	return code.str();
}

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
		if (seg == "constant") {
			code << ASM::DCHG::stack_push(idx);
		}
		/*
		else if (seg == "local") {
			code << stack_push("LCL", idx);
		}
		else if (seg == "argument") {
			code << stack_push("ARG", idx);
		}
		else if (seg == "this") {
			code << stack_push("THIS", idx);
		}
		else if (seg == "that") {
			code << stack_push("THAT", idx);
		}
		else if (seg == "static") {
			code << assign_static(m_f_name, idx);
		}
		*/
		else {
			auto error_msg = std::format("Invalid segment type: [{}].", seg);
			throw std::invalid_argument(error_msg);
		}
		break;
	case CmdType::C_POP:
		code << "// pop" << seg << " " << idx << std::endl;
		/*
		if (seg == "local") {
			code << stack_pop("LCL", idx);
		}
		else if (seg == "argument") {
			code << stack_pop("ARG", idx);
		}
		else if (seg == "this") {
			code << stack_pop("THIS", idx);
		}
		else if (seg == "that") {
			code << stack_pop("THAT", idx);
		}
		else {
			auto error_msg = std::format("Invalid segment type: [{}].", seg);
			throw std::invalid_argument(error_msg);
		}
		*/
		break;
	default:
		throw std::invalid_argument("Invalid command type.");
		break;
	}
	m_f_asm << code.str();
}

// ============================================================ //
