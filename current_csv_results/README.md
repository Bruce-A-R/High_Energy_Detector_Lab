# CSV Results from spectrum_reader.py

This folder holds the results I get from running spectrunm_reader.py for each detector.
The names for each csv file match with the detector they are from.

File contents, for each peak: 

cols: Peak energies (KeV units), peak location (in detector channel units), peak FWHM (detector channel units), peak amplitude (in counts/sec), angle of source to detector, uncertainty of fit, and FWHM (in KeV units)

There are also graphs from all the results I've gotten from running our data through our pipeline. - Bruce

fit line equations: 

NaITi: E = 2.3093136412780226(channel number) - 6.901893925899741

BGO: E = 2.2212574990748446(channel number) + 16.439734589370815

CdTe: E = 3.2262635751803947(channel number) - 204.743145190812

# Figures: 

There are also a number of figures produced all the scripts which are named for the detector the data is from and what the plot shows. 

There are also screenshots of printouts from efficiencies.py since the output of that script is text rather than a spreadsheet

# Note

All results here are from me running the code on my terminal, and there has been sucess having other group members clone and run the repo with limited testing. - Bruce
