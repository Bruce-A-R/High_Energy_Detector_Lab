"""
angular_effects.py

This funtion will use results from spectrum_reader.py to make plots of the amplitude of peaks (in counts/sec) by the angle
to be used to characterise the detector's off axis response

Inputs: 
1. csv or xls file of results from spectrum_reader
2. name of detector used

Outputs: 
1. Plot of peak amplitude of Am (a well defined peak in all detectors) by energy
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.optimize import curve_fit
import pandas as pd

def plot_amplitudes(table, detector):
    """Function to plot peak amplitudes by angle, with a fit line"""

    #INCLUDE RIGHT HERE THE FITTING 

    plt.close("all")
    ax, plt = plt.subplots(figsize = (10, 8))

    ax.set_title(f"Characterizing {detector} Detector Off-Axis Response")
    ax.set_xlabel("Angle (deg)")
    ax.set_ylabel("Peak Amplitude (counts/sec)")

    ax.scatter(table["angle"], table["amp"], label = "data")

    ax.legend()
    plt.show()

def main(csv, detector):
    """Main function to run what the script does"""

    table = pd.read_csv(csv)
    plot_amplitudes(table, detector)
    

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='''This script will return csv files of results used 
    to characterize a detector based on given data files''')
    parser.add_argument('csv', type = str, help = "path to csv", default = None)
    parser.add_argument('detector', type = str, help = "name of detector used", default = None)
    args = parser.parse_args()

    main(args.csv args.detector)

