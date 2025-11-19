
"""
spectrum_reader.py

This will read in spe or mca files from our detectors, subtract the background, then characterise the energy-detector channel
relationship for the detector. The function will return a csv of peaks by their energy, location in terms of detector channel, 
peak FHWM, and peak amplitude

How to use function:
Run with the following necessary arguments: 
    1. path to data files
    2. name of background file
    3. name of detector: "NaITi", "BGO", or "CdTe"

Outputs:
    1. results csv file
    2. plots of the energy characterization
"""
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy
from scipy.optimize import curve_fit
import pandas as pd

from glob import glob
import argparse

def file_type_checker(filename):
    """Checks the file type, because the header will have diff formatting"""

    if filename[-3:] == "Spe":
        return "Spe"
    elif filename[-3:] == "mca":
        return "mca"
    else: return "error"

def file_parser(filename):

    #the function will fill and return these dictionaries:

    header_dict = {
        "DATE_MEAS": [],
        "MEAS_TIME": []
    }

    spectrum_dict = {
        "bins": [], 
        "counts": []
    }

    if file_type_checker(filename) == "Spe" :
        IS_DATA = False

        with open(filename, "r") as file:
            for line in file:
                line = line.strip()

            # if it's data, reset the flag
                if line == '$DATA:':
                    IS_DATA = True
                    continue
                elif line.startswith('$MEAS_TIM:'):
                    next_line = next(file).split(" ")
                    header_dict["MEAS_TIME"].append(float(next_line[0]))
                    IS_DATA = False
                elif line.startswith('$DATE_MEA:'):
                    next_line = next(file).strip()
                    header_dict["DATE_MEAS"].append(next_line)
                    IS_DATA = False

            #this is for all lines following # DATA
            #while IS_DATA == True:  
                if IS_DATA == True:
                    try:
                        spectrum_dict["counts"].append(float(line))
                    except ValueError:
                        continue   
        #change if bin range changes
        for i in range(len(spectrum_dict["counts"])):
            spectrum_dict["bins"].append(i)

        return header_dict, spectrum_dict

    elif  file_type_checker(filename) == "mca" :
        IS_DATA = False

        with open(filename, "r") as file:
            for line in file:
                line = line.strip()

                # if it's data, reset the flag
                if line.startswith('<<DATA>>'):
                    IS_DATA = True
                    continue
                elif line.startswith('REAL_TIME'):
                    line = line.strip()
                    header_dict["MEAS_TIME"].append(float(line[12:]))
                    IS_DATA = False
                elif line.startswith('START_TIME'):
                    line = line.strip()
                    header_dict["DATE_MEAS"].append(line[13:])
                    IS_DATA = False
                elif line.startswith("<<END>>"):
                    IS_DATA = False

                if IS_DATA == True:
                    try:
                        spectrum_dict["counts"].append(int(line))
                    except Exception as e:
                        print(e)
                        continue   
        #change if bin range changes
        for i in range(len(spectrum_dict["counts"])):
            spectrum_dict["bins"].append(i)

        return header_dict, spectrum_dict

    elif file_type_checker(filename) == "error":
        print("give me the right file type (mca or spe) pretty please!")

def background_subtract(data, background):
    """
    Converts spectrum to units of counts/sec then subtracts background from data
    Inputs: data file, backgound file (.spe or .mca files)
    Outputs: returns dataframe object of bins and counts per second of background subtracted spectra and plot of bins by counts/sec
    """
    data_header, data_spectrum = file_parser(data)
    background_header, background_spectrum = file_parser(background)

    background_ct = background_header["MEAS_TIME"]
    data_ct = data_header["MEAS_TIME"]

    background_subtracted = (np.array(data_spectrum["counts"]) / data_ct) - (np.array(background_spectrum["counts"]) / background_ct)

    table = {
        'bins' : data_spectrum["bins"],
        'counts/sec' : background_subtracted
    }

    return pd.DataFrame(table)

def peak_finder(table):
    """finds peaks in data"""

    max_point = np.argmax(table["counts/sec"][10:]) #ignores the first ten bins incase of weird detector noise

    return int(max_point)

def ignore_peak(flux):
    """
    Function used to ignore the peak part of the data for plotting the baseline
    Input: y data (flux)
    Output: list of ajdusted y data, were values associated with the peak are replaced with mean flux
    """
    background_y = []
    mean_flux = np.mean(flux)
    flux_std = np.std(flux)
    for i in flux:
        if i < (0.5 * flux_std):
            background_y.append(i)
            background_mean = np.mean(background_y) #make a mean background level
        elif background_y == []:
            background_y.append(mean_flux)
        else:
            background_mean = np.mean(background_y)
            background_y.append(background_mean)
       # if i > 0.5 * (flux_std): #if the flux is higher than this, the point is probably part of the peak
      #      background_y.append(mean_flux) 
       #else:
        #    background_y.append(i)
    return background_y

#fitting functions: 
def quadratic(x, a, b, c):
    """A quatratic function, used for curve fitting"""
    return a * (x**2) + b * x + c

def gaussian(x, mu, sig, amp):
    """A Gaussian function, used for scipi curve fit"""
    return amp * np.exp(-0.5 * (x-mu)**2 / sig**2) / np.sqrt(2 * np.pi * sig**2)

def compound_model(x, mu, sig, amp, a, b, c):
    """Combines the quadratic fit of the background with the Gaussian fit which better represents the peak"""
    return quadratic(x, a, b, c) + gaussian(x, mu, sig, amp)

def fit_compound_model(x, y, p0=None):
    """
    Function to fit data using curve_fit and compound_model
    Inputs: x, y (list of x, y data)
    Outputs: popt (parameters array), pcov (covarience array) 
    """

    #if no p0 is passed, guess: 

    if p0 is None: 
        A_guess = np.max(y) - np.min(y)
        mu_guess = np.sum(x * y) / np.sum(y)
        sigma_guess = (np.max(x) - np.min(x)) / 10
        #getting the polynomial parameters: 
        background_y = ignore_peak(y)
        b_popt, b_pcov = curve_fit(quadratic, x, background_y, p0 = None)

    p0 = [mu_guess, sigma_guess, A_guess, *b_popt]
    popt, pcov = curve_fit(compound_model, x, y, p0 = p0)

    return popt, pcov


def gauss_fitter(table, peak_range):
    """
    Function to fit a gaussian to data and find the location of peaks
    Input: table of bins and counts/sec for a spectrum and a range of interest to look for peaks in
    Output: mu0, singma0, and amp from the gaussian fit
    """

    background_y = ignore_peak(table["counts/sec"][peak_range])
    b_popt, b_pcov = curve_fit(quadratic, table["bins"][peak_range], background_y, p0 = None)
    quad_fit = quadratic(np.array(table["bins"][peak_range]), *b_popt)

    #fitting and plotting gauss model: 
    popt, pcov = fit_compound_model(np.array(table["bins"][peak_range]), np.array(table["counts/sec"][peak_range]))
    gauss_fit = gaussian(np.array(table["bins"][peak_range]), *popt[:3])

    #returning peak location, sigma, and amplitude: 
    return popt[0], popt[1], popt[2]

def subtract_and_fit(data, background, peak_range):
    """
    Function to subtract background from a sepctrum then fit a peak within a given range
    Inputs: spectrum data, background spectrum data, range to look for peak at
    Outputs: peak location, sigma0, and amplitude from the fit. 
    """
    bg_sub_table = background_subtract(data, background)
    mu0, sigma, amp = gauss_fitter(bg_sub_table, peak_range)

    return mu0, sigma, amp

def make_results_dict(filepath, background, detector):
    """
    Funtion to take in a path to all the spectrum readings we'll use from a given detector, parse them, fit to specific ranges for peaks 
    for a given source in the file name, and append fit results to a dictionary for use characterizing the detector
    Inputs: path to files, config file? (RIGHT NOW I AM HARDCODING THAT PART), detector input as string
    Outputs: a pandas data frame

    Note: this is the stupidest function I've ever made and atm it entirely relies on having the same naming convention for all files
    but we DO have that so it works 
    """
    #dictionary of results to fill
    results = {
        'energy' : [],
        'peak loc' : [],
        'FWHM' : [],
        'amp' : []
    }


    if detector == "NaITi":
        #THIS IS HARDCODED RN AND SHOULD BE FROM CONFIG FILE
        energies = { 
            #'Co' : [1173.228, 1332.492],  Co NOT USED FOR THIS DETECTOR THE PEAKS SUCK
            'Cs' : [661.657],
            'Ba' : [80.9979, 356.0129],
            'Am' : [59.5409]
        }

        ranges = {
            'Cs' : [range(225, 400)],
            'Ba' : [range(22, 85), range(90,200)],
            'Am' : [range(0,60)]
        }

        datafiles = glob(filepath + '*.Spe')

        for file in datafiles:
            if 'Cs' in file:
                mu, sig, amp = subtract_and_fit(file, background, ranges['Cs'][0])
                results['energy'].append(energies['Cs'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)
            elif 'Ba' in file:
                mu0, sig0, amp0 = subtract_and_fit(file, background, ranges['Ba'][0])
                results['energy'].append(energies['Ba'][0])
                results['peak loc'].append(mu0)
                results['FWHM'].append(2.355 * np.abs(sig0))
                results['amp'].append(amp0)

                mu1, sig1, amp1 = subtract_and_fit(file, background, ranges['Ba'][1])
                results['energy'].append(energies['Ba'][1])
                results['peak loc'].append(mu1)
                results['FWHM'].append(2.355 * np.abs(sig1))
                results['amp'].append(amp1)
            elif 'Am' in file: 
                mu, sig, amp = subtract_and_fit(file, background, ranges['Am'][0])
                results['energy'].append(energies['Am'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)

    elif detector == "BGO":
        energies = { 
            'Co' : [1173.228],
            'Cs' : [661.657],
            'Ba' : [80.9979, 356.0129],
            'Am' : [59.5409]
        }

        ranges = {
            'Co' : [range(470, 600)],
            'Cs' : [range(210, 350)],
            'Ba' : [range(20, 50), range(100,200)],
            'Am' : [range(0,60)]
        }

        datafiles = glob(filepath + '*.Spe')

        for file in datafiles:
            if 'Co' in file:
                mu, sig, amp = subtract_and_fit(file, background, ranges['Co'][0])
                results['energy'].append(energies['Co'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)
            elif 'Cs' in file:
                mu, sig, amp = subtract_and_fit(file, background, ranges['Cs'][0])
                results['energy'].append(energies['Cs'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)
            elif 'Ba' in file:
                mu0, sig0, amp0 = subtract_and_fit(file, background, ranges['Ba'][0])
                results['energy'].append(energies['Ba'][0])
                results['peak loc'].append(mu0)
                results['FWHM'].append(2.355 * np.abs(sig0))
                results['amp'].append(amp0)

                mu1, sig1, amp1 = subtract_and_fit(file, background, ranges['Ba'][1])
                results['energy'].append(energies['Ba'][1])
                results['peak loc'].append(mu1)
                results['FWHM'].append(2.355 * np.abs(sig1))
                results['amp'].append(amp1)
            elif 'Am' in file: 
                mu, sig, amp = subtract_and_fit(file, background, ranges['Am'][0])
                results['energy'].append(energies['Am'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)

    elif detector == "CdTe":
        energies = { 
            'Cs' : [661.657],
            'Ba' : [53.1622, 383.8485],
            'Am' : [59.5409]
        }


        ranges = {
            'Cs' : [range(200, 250)],
            'Ba' : [range(0, 80), range(200, 300)], # range(230, 300)], #range(500,600)],
            'Am' : [range(100, 200)]
        }

        datafiles = glob(filepath + '*.mca')

        for file in datafiles:
            if 'Cs' in file:
                mu, sig, amp = subtract_and_fit(file, background, ranges['Cs'][0])
                results['energy'].append(energies['Cs'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)
            elif 'Ba' in file:
                mu0, sig0, amp0 = subtract_and_fit(file, background, ranges['Ba'][0])
                results['energy'].append(energies['Ba'][0])
                results['peak loc'].append(mu0)
                results['FWHM'].append(2.355 * np.abs(sig0))
                results['amp'].append(amp0)

                mu1, sig1, amp1 = subtract_and_fit(file, background, ranges['Ba'][1])
                results['energy'].append(energies['Ba'][1])
                results['peak loc'].append(mu1)
                results['FWHM'].append(2.355 * np.abs(sig1))
                results['amp'].append(amp1)
            elif 'Am' in file: 
                mu, sig, amp = subtract_and_fit(file, background, ranges['Am'][0])
                results['energy'].append(energies['Am'][0])
                results['peak loc'].append(mu)
                results['FWHM'].append(2.355 * np.abs(sig))
                results['amp'].append(amp)

    else: 
        print("Spell the Name of the Detector Right PLease: NaITi, BGO, or CdTe.")

    return pd.DataFrame(results)

def line(x, m, b):
    """linear function to use in fitting"""
    return m * x + b                   

def linear_fit(x_data, y_data, model):
    """Function to fit a line to points using curve_fit"""
    popt, pcov = curve_fit(model, x_data, y_data)
    return popt

def fit_energies(dictionary):
    """
    Function to fit energies to channel numbers using curvefit
    Input: dictionary of results from make_results_dict
    Output: slope and intercept of channel-energy relation line
    """

    popt = linear_fit(dictionary['peak loc'], dictionary['energy'], line)
    fit_line = line(dictionary['peak loc'], popt[0], popt[1])

    plt.close("all")
    fig, ax = plt.subplots(figsize = (8, 8))

    ax.set_title("Detector peak energy by channel number")
    ax.set_xlabel("Channel Number")
    ax.set_ylabel("Energy (keV)")
    ax.scatter(dictionary['peak loc'], dictionary['energy'], label = "data")
    ax.plot(dictionary['peak loc'], fit_line, ls = "-", color = "red", label = "fit line")
    ax.legend()
    plt.show()

    print(f"Slope: {popt[0]} and Intercept: {popt[1]}")

    return popt[0], popt[1]

def main(data_path, bg_path, detector):
    """Main function to run what the script does"""
    dictionary = make_results_dict(data_path, bg_path, detector)
    slope, intercept = fit_energies(dictionary)

    #adding FWHM in terms of energy to dictionary: 
    dictionary["FWHM (keV)"] = line(dictionary["FWHM"], slope, intercept)

    print(f"Slope of energy fit: {slope} Intercept of energy fit: {intercept}")

    csv_name = f"{detector} + results.csv"

    #writing results to csv: 
    dictionary.to_csv(csv_name, index=False)  



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='''This script will return csv files of results used 
    to characterize a detector based on given data files''')
    parser.add_argument('data_path', type = str, help = "path to the folder with data files", default = None)
    parser.add_argument('bg_path', type = str, help = "background spectrum file", default = None)
    parser.add_argument('detector', type = str, help = "name of detector used", default = None)
    args = parser.parse_args()

    main(args.data_path, args.bg_path, args.detector)

