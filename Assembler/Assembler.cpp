/*
* Purpose: The Hack Assembler (assembly code to binary code)
* Author : Xi (Ronnie) Chen
* Date   : 05/28/2022
* Usage  : prompt> Assembler Prog.asm
*/

#include <iostream>
#include <fstream>
#include <format>
#include <exception>
#include <filesystem>
#include <algorithm>
#include <cctype>

#include <string>
#include <vector>

#include <boost/program_options.hpp>

#include "Parser.hpp"
#include "Code.hpp"
#include "SymbolTable.hpp"
#include "types.hpp"
#include "utils.hpp"

namespace fs = std::filesystem;
namespace po = boost::program_options;

// ============================================================ //

int main(int argc, char** argv)
{
	// -------------------------------------------------------- //
	// argparse: get the name of the input source file
	// -------------------------------------------------------- //

	po::options_description desc{ "Hack Assembler" };

	desc.add_options()
		("help", "produce help message")
		("asm-file", po::value<std::string>(), "hack assembly code file")
	;

	po::positional_options_description p;
	p.add("asm-file", -1);
	
	po::variables_map vm;        
	po::store(po::command_line_parser(argc, argv).options(desc).positional(p).run(), vm);
	po::notify(vm);

	if (vm.count("help")) {
		std::cout << desc << std::endl;
	    return 0;
	}

	if (vm.count("asm-file") == 0) {
		std::cout << "Please provide a hack assemply code file!" << std::endl;
		std::cout << "Usage: HackAsm.exe Prog.asm" << std::endl;
		return 1;
	}

	fs::path asm_file_path{ vm["asm-file"].as<std::string>() };

	// -------------------------------------------------------- //
	// prepare the output file (.hack)
	// -------------------------------------------------------- //

	fs::path hack_file_path = asm_file_path;
	hack_file_path.replace_extension("hack");
	std::ofstream f_hack(hack_file_path);
	if (!f_hack.is_open()) {
		std::cout << "Failed to open [" << hack_file_path.string() << "]\n";
		return 1;
	}

	// -------------------------------------------------------- //
	// asm file processing
	// -------------------------------------------------------- //

	try {
		Parser parser{ asm_file_path };
		// check_parser(parser);
		Code code;

		// 1st pass: construct the symbol table
		std::cout << "Constructing the symbol table... ";
		SymbolTable symbol_tbl{};
		symbol_tbl.init(asm_file_path);
		std::cout << "done..." << std::endl;

		// 2nd pass: translate symbols to bits
		std::cout << "Parsing [" << asm_file_path.string() << "]... ";
		while (parser.has_more_lines()) {
			parser.advance();
			if (!parser.is_curr_instruct_valid()) {
				continue;
			}
			switch (parser.instruction_type())
			{
			case InstructType::A_INSTRUCTION: 
			{
				auto symbol = parser.symbol();
				bool is_address = std::all_of(
					symbol.begin(), symbol.end(), 
					[](unsigned char c) { return std::isdigit(c); }
				);
				if (is_address) {
					f_hack << "0" << code.symbol(symbol) << std::endl;
				}
				else {  // either a variable or a label
					auto address = symbol_tbl.get_address(symbol);
					f_hack << "0" << code.symbol(address) << std::endl;
				}
				break;
			}
			case InstructType::C_INSTRUCTION:
			{
				f_hack << "111"
					<< code.comp(parser.comp())
					<< code.dest(parser.dest())
					<< code.jump(parser.jump())
					<< std::endl;
				break;
			}
			case InstructType::L_INSTRUCTION:
				continue;
				break;
			case InstructType::INVALID:
				std::cout << "Invalid syntax: " << parser.get_curr_instruct() << std::endl;
				continue;
				break;
			default:
				std::cout << "Unimplemented InstructType encountered!" << std::endl;
				continue;
				break;
			}
		}
		std::cout << "done..." << std::endl;

		std::cout << "File written to: " << hack_file_path.string() << std::endl;
	}
	catch (const std::exception& e) {
		std::cout << e.what() << std::endl;
		return 1;
	}

	// -------------------------------------------------------- //
	// clean-ups
	// -------------------------------------------------------- //

	f_hack.close();

	// -------------------------------------------------------- //

	return 0;
}

// ============================================================ //