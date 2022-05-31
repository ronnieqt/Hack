// Purpose: translating the fields (symbolic mnemonics) into binary codes

#pragma once

#include <string>
#include <unordered_map>
#include <bitset>

using string_map = std::unordered_map<std::string, std::string>;

// ============================================================ //

class Code
{
private:
	static const string_map m_d_table;
	static const string_map m_c_table;
	static const string_map m_j_table;

public:
	Code() = default;
	~Code() = default;

	std::string symbol(const std::string& s) const
	{
		auto i = std::stoi(s);
		auto b = std::bitset<15>(i);
		return b.to_string();
	}
	std::string symbol(int address) const
	{
		auto b = std::bitset<15>(address);
		return b.to_string();
	}
	std::string dest(const std::string& d) const
	{
		return m_d_table.at(d);
	}
	std::string comp(const std::string& c) const
	{
		return m_c_table.at(c);
	}
	std::string jump(const std::string& j) const
	{
		return m_j_table.at(j);
	}
};

// ============================================================ //

const string_map Code::m_d_table = {
	{   "", "000"},
	{  "M", "001"},
	{  "D", "010"},
	{ "DM", "011"},
	{ "MD", "011"},
	{  "A", "100"},
	{ "AM", "101"},
	{ "MA", "101"},
	{ "AD", "110"},
	{ "DA", "110"},
	{"ADM", "111"},
	{"AMD", "111"},
	{"DAM", "111"},
	{"DMA", "111"},
	{"MAD", "111"},
	{"MDA", "111"},
};

const string_map Code::m_c_table = {
	{  "0", "0101010"},
	{  "1", "0111111"},
	{ "-1", "0111010"},
	{  "D", "0001100"},
	{  "A", "0110000"},
	{ "!D", "0001101"},
	{ "!A", "0110001"},
	{ "-D", "0001111"},
	{ "-A", "0110011"},
	{"D+1", "0011111"},
	{"A+1", "0110111"},
	{"D-1", "0001110"},
	{"A-1", "0110010"},
	{"D+A", "0000010"},
	{"D-A", "0010011"},
	{"A-D", "0000111"},
	{"D&A", "0000000"},
	{"D|A", "0010101"},
	{  "M", "1110000"},
	{ "!M", "1110001"},
	{ "-M", "1110011"},
	{"M+1", "1110111"},
	{"M-1", "1110010"},
	{"D+M", "1000010"},
	{"D-M", "1010011"},
	{"M-D", "1000111"},
	{"D&M", "1000000"},
	{"D|M", "1010101"},
};

const string_map Code::m_j_table = {
	{   "", "000"},
	{"JGT", "001"},
	{"JEQ", "010"},
	{"JGE", "011"},
	{"JLT", "100"},
	{"JNE", "101"},
	{"JLE", "110"},
	{"JMP", "111"},
};

// ============================================================ //
