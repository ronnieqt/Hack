// implementation details fo the VM parser

#include "Parser.hpp"

#include <cassert>
#include <vector>

#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string_regex.hpp>

using namespace boost::algorithm;

// ============================================================ //

// static data members
const std::set<std::string> Parser::m_al_cmds{
	"add", "sub", "neg",
	"eq", "gt", "lt",
	"and", "or", "not"
};

// ============================================================ //

void format_input(std::string& input)
{
	// remove comments
	boost::regex re{ "//.*$" };
	erase_regex(input, re);
	// trim white spaces
	trim(input);
}

// ============================================================ //

bool Parser::has_more_lines() const
{
	// Are there more lines in the ipnut?
	return !m_f_vm.eof();
}

// ============================================================ //

void Parser::advance()
{
	// Reads the next instruction from the input, and
	//     makes it the current command
	while (has_more_lines()) {
		// keep advancing until a valid command is found
		// or no more lines are available
		std::getline(m_f_vm, m_curr_cmd);
		format_input(m_curr_cmd);
		if (is_curr_cmd_valid()) {
			break;
		}
	}
}

// ============================================================ //

CmdType Parser::command_type() const
{
	if (m_al_cmds.contains(m_curr_cmd)) {
		return CmdType::C_ARITHMETIC;
	}
	else if (m_curr_cmd.starts_with("push")) {
		return CmdType::C_PUSH;
	}
	else if (m_curr_cmd.starts_with("pop")) {
		return CmdType::C_POP;
	}
	// TODO: label, goto, if, func, ret, call
	else {
		return CmdType::C_INVALID;
	}
}

// ============================================================ //

std::string Parser::arg1() const
{
	assert(command_type() != CmdType::C_RETURN);
	// returns the first arg of the current cmd
	auto cmd_t = command_type();
	if (cmd_t == CmdType::C_ARITHMETIC) {
		return m_curr_cmd;
	}
	else if (cmd_t == CmdType::C_PUSH || cmd_t == CmdType::C_POP) {
		std::vector<std::string> parts;
		split(parts, m_curr_cmd, is_space());
		return parts[1];
	}
	else {
		return "INVALID";
	}
}

// ============================================================ //

int Parser::arg2() const
{
	auto curr_cmd_type = command_type();
	assert(
		curr_cmd_type == CmdType::C_PUSH  
		|| curr_cmd_type == CmdType::C_POP 
		|| curr_cmd_type == CmdType::C_FUNCTION 
		|| curr_cmd_type == CmdType::C_CALL
	);
	// returns the second arg of the current cmd
	std::vector<std::string> parts;
	split(parts, m_curr_cmd, is_space());
	return std::stoi(parts[2]);
}

// ============================================================ //

bool Parser::is_curr_cmd_valid() const
{
	bool is_empty = m_curr_cmd.empty();
	bool is_comment = m_curr_cmd.starts_with("//");
	return !is_empty && !is_comment;
}

// ============================================================ //

std::string Parser::get_curr_cmd() const
{
	return m_curr_cmd;
}

// ============================================================ //
