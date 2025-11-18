# High_Energy_Detector_Lab

Group Members: Bruce, Eris, Flora, Orlaith 

Files used are in folders seperated by detector named for each detector. There is also a folder for screenshots from the computers we used to take data with the detectors and a seperate folder for 
notebooks and scripts that are not a part of our final analysis pipeline but were created while we were figuring everything out. 

# Pipeline

The pipeline needs to be run individually for each detector. 

image of pipeline: 
<img width="415" height="344" alt="image" src="https://github.com/user-attachments/assets/4240fae3-d861-46e4-a60e-7a5cfe7022ca" />

# Instructions for using scripts

1. spectrum_reader.py: used to calibrate a detector. Run seperately for each detector with three arguments: "path to folder with spectrum files" "path to background spectrum" "detector name"
2. efficiencies.py: used to find the absolute and intrinsic efficiences. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name"
3. resolution.py: used to determine the energy resolution. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name"
4. angular_effects.py: used to characterize angular effecs. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name"

files, code, ect. should be in folders named for each detector. 
Hopefully aside from that we can all remember the naming conventions used for each thing

