# High_Energy_Detector_Lab

Group Members: Bruce, Eris, Flora, Orlaith 

Files used are in folders seperated by detector named for each detector. There is also a folder for screenshots from the computers we used to take data with the detectors and a seperate folder for 
notebooks and scripts that are not a part of our final analysis pipeline but were created while we were figuring everything out. 

References/Citations: 
1. AI was used to generate some code used in this assignment in efficiencies.py
2. Code found on GeeksforGeeks and Stack Overflow was also used in resolution.py, which may also contain AI generated responses. 

# Pipeline

The pipeline needs to be run individually for each detector. 

<img width="415" height="344" alt="image" src="https://github.com/user-attachments/assets/4240fae3-d861-46e4-a60e-7a5cfe7022ca" />

For the efficenacy and resolution results, run the pipeline using the resulting csvs from spectrum_reader using unangled measreuments. For the angular effects use spectrum_reader outputs from angles measurements. 

# Instructions for using scripts

1. spectrum_reader.py: used to calibrate a detector. Run seperately for each detector with three arguments: "path to folder with spectrum files" "path to background spectrum" "detector name". Outputs a csv file of results
2. efficiencies.py: used to find the absolute and intrinsic efficiences. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name". Outputs plots and text information
3. resolution.py: used to determine the energy resolution. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name". Outputs plots and test information. 
4. angular_effects.py: used to characterize angular effecs. Run seperately for each detector with the following arguments: "path to csv of results from spectrum_reader" "detector name". Outputs plots and text information. 

