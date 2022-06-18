// Parser: to make sense out of each VM command,
//         understand what the command seeks to.
// 
// The parser provides services for reading a VM command,
//     unpacking the command into its various components,
//     and providing convenient access to these components.

#pragma once

#include <fstream>
#include <filesystem>
#include <format>
#include <string>
#include <set>

#include "types.hpp"

namespace fs = std::filesystem;

// ============================================================ //

class Parser
{
private:
	const static std::set<std::string> m_al_cmds;

private:
	std::ifstream m_f_vm;
	std::string m_curr_cmd;

public:
	Parser(const fs::path& vm_file_path)
	{
		m_f_vm.open(vm_file_path);
		if (!m_f_vm.is_open()) {
			auto error_msg = std::format("Failed to open [{}]", vm_file_path.string());
			throw std::ios_base::failure(error_msg);
		}
	}
	~Parser()
	{
		if (m_f_vm.is_open()) {
			m_f_vm.close();
		}
	}

	bool has_more_lines() const;       // are there more lines in the input
	void advance();                    // read the next command from the input
	CmdType command_type() const;      // returns the type of the current cmd
	std::string arg1() const;          // returns the 1st argument of the current cmd
	int arg2() const;                  // returns the 2nd argument of the current cmd

	bool is_curr_cmd_valid() const;    // check if the current cmd is valid or not
	std::string get_curr_cmd() const;  // return the current command
};

// ============================================================ //
