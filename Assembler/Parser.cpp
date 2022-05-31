// Implementation details of the Parser

#include "Parser.h"

#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string_regex.hpp>

using namespace boost::algorithm;

// ============================================================ //

void format_input(std::string& input)
{
	// remove in-line comments
	boost::regex re{ "//.*$" };
	erase_regex(input, re);
	// remove white space
	erase_all(input, " ");
}

// ============================================================ //

bool Parser::has_more_lines() const
{
	// Are there more lines in the ipnut?
	return !m_f_asm.eof();
}

// ============================================================ //

void Parser::advance()
{
	// Skips over white space and comments
	// Reads the next instruction from the input, and
	//     makes it the current intruction
	// This routine should be called only if has_more_lines() is true
	// Initially, there is no current instruction
	// NOTE:
	// This function will assign "" to m_curr_instruct when
	//     the provided .asm file has trailling empty lines.
	while (has_more_lines()) {
		std::getline(m_f_asm, m_curr_instruct);
		format_input(m_curr_instruct);
		if (is_curr_instruct_valid()) {
			break;
		}
	}
}

// ============================================================ //

InstructType Parser::instruction_type() const
{
	// Returns the type of the current instruction
	// A_INSTRUCTION: @xxx
	// C_INSTRUCTION: dest=comp;jump
	// L_INSTRUCTION: (xxx)
	if (!is_curr_instruct_valid()) {
		return InstructType::INVALID;
	}
	else if (m_curr_instruct[0] == '@') {
		return InstructType::A_INSTRUCTION;
	}
	else if (m_curr_instruct[0] == '(') {
		return InstructType::L_INSTRUCTION;
	}
	else {
		// assumptions: 
		// Prog.asm is error-free
		// There are only 3 types of intruction: A, L, and C
		return InstructType::C_INSTRUCTION;
	}
}

// ============================================================ //

std::string Parser::symbol() const
{
	// If the current instruction is (xxx), returns the symbol xxx
	// If the current instruction is @xxx , returns the symbol or decimal xxx (as a string)
	// Should only be called on A_ or _L_INSTRUCTION
	switch (instruction_type())
	{
	case InstructType::A_INSTRUCTION:
		return m_curr_instruct.substr(1);
	case InstructType::L_INSTRUCTION:
		return trim_copy_if(m_curr_instruct, is_any_of("()"));
	default:
		throw std::domain_error("symbol() called on a wrong instruction type");
	}
}

// ============================================================ //

std::string Parser::dest() const
{
	// Returns the symbolic dest part of the current instruction
	// Should be called on C_INSTRUCTION
	if (instruction_type() == InstructType::C_INSTRUCTION) {
		auto n = m_curr_instruct.find_first_of('=');
		if (n != std::string::npos) {
			return m_curr_instruct.substr(0, n);
		}
		else {
			return "";
		}
	}
	else {
		throw std::domain_error("dest() called on a wrong instruction type");
	}
}

// ============================================================ //

std::string Parser::comp() const
{
	// Returns the symbolic comp part of the current instruction
	// Should be called on C_INSTRUCTION
	if (instruction_type() == InstructType::C_INSTRUCTION) {
		auto n1 = m_curr_instruct.find_first_of('=');
		auto n2 = m_curr_instruct.find_first_of(';');
		if (n1 != std::string::npos && n2 != std::string::npos && n1 < n2) {
			return m_curr_instruct.substr(n1 + 1, n2 - n1 - 1);
		}
		else if (n1 != std::string::npos) {
			return m_curr_instruct.substr(n1 + 1);
		}
		else if (n2 != std::string::npos) {
			return m_curr_instruct.substr(0, n2);
		}
		else {
			return "";
		}
	}
	else {
		throw std::domain_error("dest() called on a wrong instruction type");
	}
}

// ============================================================ //

std::string Parser::jump() const
{
	// Returns the symbolic jump part of the current instruction
	// Should be called on C_INSTRUCTION
	if (instruction_type() == InstructType::C_INSTRUCTION) {
		auto n = m_curr_instruct.find_first_of(';');
		if (n != std::string::npos) {
			return m_curr_instruct.substr(n+1);
		}
		else {
			return "";
		}
	}
	else {
		throw std::domain_error("dest() called on a wrong instruction type");
	}
}

// ============================================================ //

std::string Parser::get_curr_instruct() const
{
	return m_curr_instruct;
}

// ============================================================ //

bool Parser::is_curr_instruct_valid() const
{
	bool is_empty = equals(m_curr_instruct, "");
	bool is_a_comment = starts_with(m_curr_instruct, "//");
	return !is_empty && !is_a_comment;
}

// ============================================================ //
