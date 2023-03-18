#include "juhrnal.hh"
#include "plot.hh"

#include <fstream>

int main()
{
	auto juhrnal= Juhrnal();

	const char *const FILENAME= "dat/all.dat";
	
	std::ofstream os(FILENAME);
	if (os.fail()) {
		perror(FILENAME); 
		exit(1);
	}

	juhrnal.output(os);

	Plot::all(juhrnal); 
	
	os.close(); 
	if (os.fail()) {
		perror(FILENAME); 
		exit(1); 
	}
	
	return 0;
}
