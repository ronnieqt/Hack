/*
* Purpose: parsing the input into instructions and
*          instructions into fields
*          encapsulating access to the input assembly code
* 
* Functionalities:
* 1. advancing through the source code (accessing the input 1 line at a time)
* 2. skipping comments and white spaces
* 3. breaking each symbolic instruction into its underlying components
*/

#pragma once

#include <iostream>
#include <fstream>
#include <filesystem>
#include <format>
#include <string>

#include "types.h"

namespace fs = std::filesystem;

// ================================================== //

class Parser
{
private:
	std::ifstream m_f_asm;
	std::string m_curr_instruct;

public:
	Parser(const fs::path& asm_file_path)
	{
		m_f_asm.open(asm_file_path);
		if (!m_f_asm.is_open()) {
			auto error_msg = std::format("Failed to open [{}]", asm_file_path.string());
			throw std::ios_base::failure(error_msg);
		}
	}
	~Parser()
	{
		if (m_f_asm.is_open()) {
			m_f_asm.close();
		}
	}

	bool has_more_lines() const;            // are there more lines in the input
	void advance();                         // read the next instruction from the input
	InstructType instruction_type() const;  // return the type of the current instruction
	std::string symbol() const;             // only be called for A_ or L_INSTRUCTION
	std::string dest() const;               // return the symbolic dest part of the current C_INSTRUCTION
	std::string comp() const;               // return the symbolic comp part of the current C_INSTRUCTION
	std::string jump() const;               // return the symbolic jump part of the current C_INSTRUCTION

	std::string get_curr_instruct() const;
	bool is_curr_instruct_valid() const;
};

// ================================================== //
