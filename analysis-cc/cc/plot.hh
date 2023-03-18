#ifndef PLOT_HH
#define PLOT_HH

#include "process.hh"

#include <memory>

#include <TGraph.h>
#include <TCanvas.h>
#include <TAxis.h>

struct Plot
{
	/* Output "plot/all.pdf" */
	static void all(const Juhrnal &); 
};

void Plot::all(const Juhrnal &juhrnal)
{
	(void) juhrnal;
	
	std::string title= "All";
	int width= 800, height= 600; /* pixels; irrelevant */

	std::vector <double> x, y;
	int offset;
	Process::all(x, y, juhrnal, offset); 

	for (double &xx: x) {
		xx *= 24 * 60 * 60;
	}
	
	TCanvas c("c", title.c_str(), 0, 0, width, height);
	TGraph gr(x.size(), &x[0], &y[0]);

	gr.SetTitle(title.c_str());
	gr.SetFillColor(40);

	TAxis *axis= gr.GetXaxis();
	axis->SetLimits(x[0], x[x.size()-1]);
	axis->SetTimeDisplay(1);
	axis->SetTimeFormat("%Y-%m");
	axis->SetTimeOffset(offset * 24 * 60 * 60, "gmt");

	gr.Draw("AB");

	c.Print("plot/all.pdf");
}

#endif /* ! PLOT_HH */
