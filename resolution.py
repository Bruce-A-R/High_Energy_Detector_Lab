
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.optimize import curve_fit
import pandas as pd
import argparse

"""
resolution.py

This script will characterize the resolution (as R^2 as a funciton of E) for a given detector

How to use function: 
Run with the following necessary arguments: 
1. csv file of results from spectrum_reader.py for all sources unangled
2. name of detector

Outputs: 
1. plot of resolution ^2 by energy with fit line equation and uncertainties (IF I GET TO THAT). 

"""

def resolution_eq(E2, a, b, c):
    """funciton to use to fit resolution^2 curve, in terms of E^2"""
    return a * E2**(-1) + b * E2**(-0.5) + c


def res_curve_fit(E, R2):
    """
    Function to fit a curve to points using curve_fit and the equation defined in resolution_eq
    Inputs: Energy and Resoltuion (unsquared) from the spectrum_reader.py data
    Outputs: popt, pcov, and error from the fit
    """
    x_data = E**2
    #R2_data = R #**2

    p0_guess = [1.0, 1.0, 0.0]
    popt, pcov = curve_fit(resolution_eq, x_data, R2, p0=p0_guess)
    perr = np.sqrt(np.diag(pcov))

    return popt, pcov, x_data, perr

def resolution_plot(csv, detector):
    """
    Function to read in a csv or xls file of datae from spectrum_reader results and plot resolution by energy
    for the peaks in the table
    Inputs: Csv file, title for plot
    Output: plot of resolution by energy for peaks in a given table
    """
    table = pd.read_csv(csv)
    table["resolution"] = table["FWHM (keV)"] / table["energy"]
    table = table.sort_values("energy")

    E = table["energy"]
    R2 = table["resolution"]**2
    R = table["resolution"]

    popt, pcov, x_data, perr = res_curve_fit(E, R2)

    #making it so the fit line is smooth instead of choppy, from GeeksforGeeks website: 
    E_linespace = np.linspace(min(table["energy"]), max(table["energy"]), 300)
    E2_linespace = E_linespace**2

    fit = resolution_eq(E2_linespace, *popt)
    
    #fit = resolution_eq(table["energy"]**2, *popt)

    plt.close("all")
    fig, ax = plt.subplots(figsize = (10,8))

    ax.set_title(f"Plotting resolution by energy for the {detector} detector")
    ax.set_xlabel("E (keV)")
    ax.set_ylabel("R^2")
    
    ax.scatter(table["energy"], table["resolution"] ** 2, label = "data")
    ax.plot(E_linespace, fit, ls = "-", color = "red", label = f"Best fit : R^2 = {popt[0]}E^(-2) + {popt[1]}E^(-1) + {popt[2]}")

    #plt.yscale("log")
    #plt.xscale("log")
    plt.tight_layout()
    plt.legend()
    plt.show()

    return popt, perr

def main(csv, detector):
    """Main function to run what the script does"""
    popt, perr = resolution_plot(csv, detector)  
    print(f"Fit line with uncertainty: R^2 = ({popt[0]} +/1 {perr[0]})E^(-2) + ({popt[1]} +/1 {perr[1]})E^(-1) + ({popt[2]} +/1 {perr[2]})")

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='''This script will return a plot of resolution by energy for given detector readings''')
    parser.add_argument('csv', type = str, help = "path to the csv", default = None)
    parser.add_argument('detector', type = str, help = "name of detector used", default = None)
    args = parser.parse_args()

    main(args.csv, args.detector)


    

