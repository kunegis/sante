#ifndef REPLACE_TABS_HH
#define REPLACE_TABS_HH

/*
 * Replace tabs by spaces, assuming 8-char tab stops, and each byte taking one
 * position.  
 */ 
std::string replace_tabs(const std::string &line)
{
	std::string ret;

	for (char c:  line) {
		if (c == '\t') {
			int count= (-ret.size()) % 8;
			assert(count >= 0 && count < 8);
			ret += std::string(count, ' '); 
		} else {
			ret += c;
		}
	}

	return ret;
}

#endif /* ! REPLACE_TABS_HH */
