// translate a parsed VM command into Hack assembly code

#pragma once

#include <filesystem>
#include <fstream>
#include <format>

#include "types.hpp"

namespace fs = std::filesystem;

// ============================================================ //

class CodeWriter
{
private:
	const std::string m_f_name;
	std::ofstream m_f_asm;

public:
	CodeWriter(const fs::path& asm_file_path)
		: m_f_name{ asm_file_path.stem().string() }
	{
		m_f_asm.open(asm_file_path);
		if (!m_f_asm.is_open()) {
			auto error_msg = std::format("Failed to open [{}]", asm_file_path.string());
			throw std::ios_base::failure(error_msg);
		}
	}
	~CodeWriter()
	{
		if (m_f_asm.is_open()) {
			m_f_asm << "(END)\n" << "@END\n" << "0;JMP\n";
			m_f_asm.close();
		}
	}

	void write_arithmetic(const std::string& cmd);
	void write_push_pop(CmdType cmd_t, const std::string& seg, int idx);
};

// ============================================================ //
