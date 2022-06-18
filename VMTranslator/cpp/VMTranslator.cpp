/*
* Program: The Hack Translator (vm code to assembly code)
* Author : Xi (Ronnie) Chen
* Date   : 06/04/2022
* Usage  : prompt> VMTranslator ProgName.vm
*/

#include <iostream>
#include <string>
#include <filesystem>

#include <boost/program_options.hpp>

#include "Parser.hpp"
#include "CodeWriter.hpp"

namespace fs = std::filesystem;
namespace po = boost::program_options;

// ============================================================ //

int main(int argc, char** argv)
{
	// -------------------------------------------------------- //
	// argparse: get the name of the input source file
	// -------------------------------------------------------- //

	po::options_description desc{ "Hack VM Translator" };

	desc.add_options()
		("help", "produce help message")
		("file", po::value<std::string>(), "hack vm code file")
	;

	po::positional_options_description p;
	p.add("file", -1);
	
	po::variables_map vm;        
	po::store(po::command_line_parser(argc, argv).options(desc).positional(p).run(), vm);
	po::notify(vm);

	if (vm.count("help")) {
		std::cout << desc << std::endl;
	    return 0;
	}

	if (vm.count("file") == 0) {
		std::cout << "Please provide a hack vm code file!" << std::endl;
		std::cout << "Usage: VMTranslator.exe Prog.vm" << std::endl;
		return 1;
	}

	fs::path vm_file_path{ vm["file"].as<std::string>() };
	fs::path asm_file_path{ vm_file_path };
	asm_file_path.replace_extension("asm");

	// -------------------------------------------------------- //
	// vm file processing
	// -------------------------------------------------------- //

	try {
		// init
		Parser parser{ vm_file_path };
		CodeWriter writer{ asm_file_path };

		// parsing
		std::cout << "Parsing [" << vm_file_path.string() << "]... ";
		while (parser.has_more_lines()) {
			parser.advance();
			if (!parser.is_curr_cmd_valid()) {
				continue;
			}
			auto cmd_t = parser.command_type();
			if (cmd_t == CmdType::C_ARITHMETIC) {
				writer.write_arithmetic(parser.arg1());
			}
			else if (cmd_t == CmdType::C_PUSH || cmd_t == CmdType::C_POP) {
				writer.write_push_pop(cmd_t, parser.arg1(), parser.arg2());
			}
			else {
				// TODO
			}
		}
		std::cout << "done..." << std::endl;

		std::cout << "File written to: " << asm_file_path.string() << std::endl;
	}
	catch (const std::exception& e) {
		std::cout << e.what() << std::endl;
		return 1;
	}

	// -------------------------------------------------------- //

	return 0;
}

// ============================================================ //