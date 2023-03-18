#ifndef JUHRNAL_HH
#define JUHRNAL_HH

#include <fstream>
#include <regex>
#include <cassert>

#include "replace_tabs.hh"
#include "date.hh"

class Juhrnal
{
public:
	Juhrnal();


	void output(std::ostream &os); 

	std::vector <std::pair <Date, std::string> > entries;
	
private:
	static constexpr const char *FILENAME= "sante/JUHRNAL"; 
};

Juhrnal::Juhrnal()
{
	std::ifstream i(FILENAME);

	std::string text_last_night;
	Date date_previous(-1, -1, -1); 

	for (std::string line; std::getline(i, line); ) {
		if (line[0] == '\0' || isspace(line[0])) {
			for (char c: line) {
				if (! isspace(c)) {
					/* Line has non-whitespace */
					fprintf(stderr, "*** Invalid line (1): %s\n", line.c_str());
					exit(1); 
				}
			}
			continue;
		}

		line= replace_tabs(line); 

		std::smatch m;

		/* Night entries */
		/* For now, the night text is prepended to the next day */
		// XXX check that the night entry is exactly between two consecutive dates
		std::regex re("night      (.*)", std::regex::extended);
		if (regex_match(line, m, re)) {
			assert(m.size() == 2); 
			text_last_night= m.str(1);
			continue;
		}
		
		std::regex re2("([0-9]{4})(      |-([0-9]{2})(  |-([0-9]{2})))(| (.*))", std::regex::extended);
		if (! regex_match(line, m, re2)) {
			fprintf(stderr, "*** Invalid line (2): %s\n",
				line.c_str()); 
			exit(1);
		}
		std::string year_string=  m.str(1);
		std::string month_string= m.str(3);
		std::string day_string=   m.str(5);

		char *endp;
		
		errno= 0;
		unsigned year_parse= strtoul(year_string.c_str(), &endp, 10);
		if (errno) { perror("strtoul"); exit(1); }
		int year= year_parse;

		int month= -1;
		if (month_string != "") {
			errno= 0;
			unsigned month_parse= strtoul(month_string.c_str(), &endp, 10);
			month= month_parse;
		}

		int day= -1;
		if (day_string != "") {
			errno= 0;
			unsigned day_parse= strtoul(day_string.c_str(), &endp, 10);
			day= day_parse;
		}

		Date date(year, month, day); 

		std::string text= m.str(7);
		if (text_last_night != "") {
			if (! (date_previous.has_day() &&
			       date_next(date_previous) == date)) {
				fprintf(stderr, "*** Night entry must be between two consecutive dates: %s\n", line.c_str()); 
				exit(1); 
			}
			text= text_last_night + " " + text;
			text_last_night= ""; 
		}

		date_previous= date; 

		entries.push_back({date, text}); 
	}
}

void Juhrnal::output(std::ostream &os)
{
	Date date_first= entries.at(0).first;
	date_first.fill(); 

	Date_Diff_Calculator ddc(date_first); 
	
	for (const auto &entry: entries) {
		Date date= entry.first;
		const std::string &text= entry.second;

		date.fill(); 

		if (! (date_first <= date)) {
			fprintf(stderr, "*** Dates not in order: %04u-%02u-%02u\n", date.year, date.month, date.day); 
			exit(1); 
		}
		
		int index= ddc.diff(date); 
		
		os << index << " " << text.length() << "\n"; 
	}
}

#endif /* ! JUHRNAL_HH */
