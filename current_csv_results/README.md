# CSV Results from spectrum_reader.py

This folder holds the results I get from running spectrunm_reader.py for each detector.
The names for each csv file match with the detector they are from.

File contents, for each peak: 

cols: Peak energies (KeV units), peak location (in detector channel units), peak FWHM (detector channel units), peak amplitude (in counts/sec), and FWHM (in KeV units)


fit line equations: 

NaITi: E = 2.3093136412780226(channel number) - 6.901893925899741

BGO: E = 2.2212574990748446(channel number) + 16.439734589370815

CdTe: E = 3.2262635751803947(channel number) - 204.743145190812
