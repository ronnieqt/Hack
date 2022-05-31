// The Symbol Table

#pragma once

#include <string>
#include <unordered_map>
#include <filesystem>

namespace fs = std::filesystem;

using int_map = std::unordered_map<std::string, int>;

// ============================================================ //

class SymbolTable
{
private:
	int_map m_symbol_table;
	int next_var_address;

public:
	SymbolTable();
	~SymbolTable() = default;

	void add_entry(const std::string& symbol, int address);
	bool contains(const std::string& symbol) const;
	int get_address(const std::string& symbol);

	void init(const fs::path& asm_file_path);
};

// ============================================================ //
