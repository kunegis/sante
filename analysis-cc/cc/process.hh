#ifndef PROCESS_HH
#define PROCESS_HH

/* 
 * Take a Juhrnal and ouptut vectors of numbers to be plotted. 
 *
 * OFFSET:  the index of the first day, in Unix time, i.e., the number of days
 * after Jan 1 1970.  
 */
struct Process
{
	static void all(std::vector <double> &x,
			std::vector <double> &y,
			const Juhrnal &,
			int &offset);
};

void Process::all(std::vector <double> &x,
		  std::vector <double> &y,
		  const Juhrnal &juhrnal,
		  int &offset)
{
	x.clear();
	y.clear(); 

	Date date_first= juhrnal.entries.at(0).first;
	date_first.fill(); 
	Date_Diff_Calculator ddc(date_first); 
	for (const auto &entry: juhrnal.entries) {
		Date date= entry.first;
		const std::string &text= entry.second;
		date.fill(); 
		int index= ddc.diff(date);
		x.push_back(index);
		y.push_back(text.length()); 
	}

	Date date_unix(1970, 1, 1);
	offset= Date_Diff_Calculator::diff(date_unix, date_first); 
}

#endif /* ! PROCESS_HH */
