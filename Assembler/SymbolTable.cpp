// Implementation Details of the Symbol Table

#include "SymbolTable.hpp"
#include "Parser.hpp"
#include "types.hpp"

#include <fstream>

// ============================================================ //

SymbolTable::SymbolTable()
	: next_var_address{ 16 }
{
	// pre-defined symbols
	m_symbol_table["R0"] = 0;
	m_symbol_table["R1"] = 1;
	m_symbol_table["R2"] = 2;
	m_symbol_table["R3"] = 3;
	m_symbol_table["R4"] = 4;
	m_symbol_table["R5"] = 5;
	m_symbol_table["R6"] = 6;
	m_symbol_table["R7"] = 7;
	m_symbol_table["R8"] = 8;
	m_symbol_table["R9"] = 9;
	m_symbol_table["R10"] = 10;
	m_symbol_table["R11"] = 11;
	m_symbol_table["R12"] = 12;
	m_symbol_table["R13"] = 13;
	m_symbol_table["R14"] = 14;
	m_symbol_table["R15"] = 15;
	m_symbol_table["SCREEN"] = 16384;
	m_symbol_table["KBD"] = 24576;
	m_symbol_table["SP"] = 0;
	m_symbol_table["LCL"] = 1;
	m_symbol_table["ARG"] = 2;
	m_symbol_table["THIS"] = 3;
	m_symbol_table["THAT"] = 4;
}

// ============================================================ //

void SymbolTable::add_entry(const std::string& symbol, int address)
{
	m_symbol_table[symbol] = address;
}

// ============================================================ //

bool SymbolTable::contains(const std::string& symbol) const
{
	return m_symbol_table.contains(symbol);
}

// ============================================================ //

int SymbolTable::get_address(const std::string& symbol)
{
	if (contains(symbol)) {
		return m_symbol_table.at(symbol);
	}
	else {
		m_symbol_table[symbol] = next_var_address;
		next_var_address++;
		return m_symbol_table[symbol];
	}
}

// ============================================================ //

void SymbolTable::init(const fs::path& asm_file_path)
{
	int pc = -1;  // the 1st instruction is indexed 0
	Parser parser{ asm_file_path };
	while (parser.has_more_lines()) {
		parser.advance();
		if (!parser.is_curr_instruct_valid()) {
			continue;
		}
		auto instruct_type = parser.instruction_type();
		if (instruct_type == InstructType::A_INSTRUCTION ||
			instruct_type == InstructType::C_INSTRUCTION) {
			pc++;
		}
		else if (parser.instruction_type() == InstructType::L_INSTRUCTION) {
			// label symbols
			add_entry(parser.symbol(), pc + 1);
		}
	}
}

// ============================================================ //
