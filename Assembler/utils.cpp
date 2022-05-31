// implementation details of utility functions

#include "utils.hpp"
#include "Parser.hpp"

// ============================================================ //

void check_parser(Parser& parser)
{
	while (parser.has_more_lines()) {
		parser.advance();
		// skip invalid instruction
		if (!parser.is_curr_instruct_valid()) {
			continue;
		}
		// print type of current instruction
		switch (parser.instruction_type())
		{
		case InstructType::A_INSTRUCTION:
			std::cout << "[A] ";
			break;
		case InstructType::L_INSTRUCTION:
			std::cout << "[L] ";
			break;
		case InstructType::C_INSTRUCTION:
			std::cout << "[C] ";
			break;
		default:
			std::cout << "[X] ";  // invalid instruction
			break;
		}
		// print current instruction
		std::cout << parser.get_curr_instruct();
		// print symbol and (dest, comp, jump)
		switch (parser.instruction_type())
		{
		case InstructType::A_INSTRUCTION:
			std::cout << " => " << parser.symbol();
			break;
		case InstructType::L_INSTRUCTION:
			std::cout << " => " << parser.symbol();
			break;
		case InstructType::C_INSTRUCTION:
			std::cout << " => "
				<< "(" << parser.dest() << ")"
				<< "(" << parser.comp() << ")"
				<< "(" << parser.jump() << ")";
			break;
		default:
			std::cout << "    Undefined!" << std::endl;
			break;
		}
		// end of printing
		std::cout << std::endl;
	}
}

// ============================================================ //
