// building blocks for asm commands

#pragma once

#include <string>

namespace ASM 
{
	// will not change the D register
	namespace DNCHG
	{
		// --- Pointer OPs --- //
		// ptr++ (ptr = ptr + 1)
		std::string ptr_pp(const std::string& ptr);
		// ptr-- (ptr = ptr - 1)
		std::string ptr_mm(const std::string& ptr);
		// *D (A = D, focus on the register who's address is stored in D)
		std::string star();
		// *ptr (A = ptr, focus on the register pointed by ptr)
		std::string star_ptr(const std::string& ptr);
		// *(ptr-1) (A = ptr - 1)
		std::string star_ptrm1(const std::string& ptr);

		// --- Stack OPs --- //
		// push value in D into stack
		std::string stack_push();

		// var = D (assign the current value in the D register to the variable 'var')
		std::string assign(const std::string& var);

		// check condition on D
		std::string if_else(
			const std::string& j_cond, 
			const std::string& t_part, 
			const std::string& f_part
		);
	}

	// will change the D register
	namespace DCHG
	{
		// --- Pointer OPs --- //
		// D = ptr + i
		std::string ptr_pi(const std::string& ptr, int i);

		// --- Stack OPs --- //
		// push val into stack
		std::string stack_push(int val);
		// D = value popped from the stack
		std::string stack_pop();
	}
}

