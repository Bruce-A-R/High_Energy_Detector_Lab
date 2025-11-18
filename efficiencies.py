
"""
efficiencies.py

This script is used to find the efficiancy of each detector, using Flora's compute_efficiencies function

Inputs: run the following necessary arguments: 
    1. script with a csv file of results from spectrum_reader (string)
    2. the name of the detector  (string)

Outputs: plots and absolute and intrinsic effficiancy for the detector 

"""
import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd

def compute_efficiencies(energies, count_rates, source_info, detector_geom, angles_deg=[0.0], plot=True):

    # Compute absolute and intrinsic efficiencies.
    activity = source_info.get('activity_Bq', None)
    branching = source_info.get('branching_ratios', None)
    
    A = detector_geom.get('area_m2', None)
    d = detector_geom.get('distance_m', None)
    
    energies = np.array(energies, dtype=float)
    areas_counts_per_s = np.array(count_rates, dtype=float)
    
    if branching is None:
        branching = np.ones_like(energies)
    else:
        branching = np.array(branching, dtype=float)
    
    # Compute geometric factor for angles
    angles = np.deg2rad(np.array(angles_deg, dtype=float))
    G_angles = []
    A_proj = A
    for theta in angles:
        A_theta = A_proj * np.cos(theta)
        G = A_theta / (4.0 * np.pi * (d**2))
        G_angles.append(G)
    G_angles = np.array(G_angles)
    
    # Compute efficiencies for theta=0
    eps_abs = areas_counts_per_s / (activity * branching)
    G0 = G_angles[0]
    eps_intrinsic = areas_counts_per_s / (activity * branching * G0)
    
    if plot:
        # Absolute efficiency vs Energy
        plt.figure(figsize=(7, 5))
        plt.scatter(energies, eps_abs, s=60)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Energy (keV)')
        plt.ylabel('Absolute efficiency (ε_abs)')
        plt.title('Absolute efficiency vs Energy')
        plt.grid(alpha=0.3, which='both')
        plt.show()
        
        # Intrinsic efficiency vs Energy (log-log fit)
        lnE = np.log(energies)
        ln_eps = np.log(eps_intrinsic)
        p = np.polyfit(lnE, ln_eps, 2)
        lnE_fit = np.linspace(lnE.min()*0.9, lnE.max()*1.1, 200)
        
        plt.figure(figsize=(7, 5))
        plt.scatter(energies, eps_intrinsic, label='Data')
        Efit = np.exp(lnE_fit)
        eps_fit = np.exp(np.polyval(p, lnE_fit))
        plt.plot(Efit, eps_fit, '-r', label=f'lnε fit: a={p[2]:.3f}, b={p[1]:.3f}, c={p[0]:.3f}')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Energy (keV)')
        plt.ylabel('Intrinsic efficiency (ε_intr)')
        plt.legend()
        plt.grid(alpha=0.3, which='both')
        plt.title('Intrinsic efficiency vs Energy (log-log)')
        plt.show()
        
        # Efficiency vs angle 
        if len(areas_counts_per_s) > 0 and len(angles_deg) > 1:
            idx = np.argmax(areas_counts_per_s)
            eps_intrinsic_angles = areas_counts_per_s[idx] / (activity * branching[idx] * G_angles)
            plt.figure(figsize=(7, 4))
            plt.plot(angles_deg, eps_intrinsic_angles, 'o-')
            plt.xlabel('Angle (deg)')
            plt.ylabel('Intrinsic efficiency (ε_intr)')
            plt.title('Intrinsic efficiency vs Angle (example peak)')
            plt.grid(alpha=0.3)
            plt.show()
    
    out = {
        'energies_keV': energies,
        'areas_counts_per_s': areas_counts_per_s,
        'branching': branching,
        'absolute_efficiency': eps_abs,
        'intrinsic_efficiency': eps_intrinsic,
        'G_angles': G_angles,
        'angles_deg': angles_deg
    }
    return out

def main(data, detector):

    table = pd.read_csv(data)
      
    # Your measured data
    energies = table["energy"]
    count_rates = table["amp"]
    
    source_info = {'activity_Bq': 37000,'branching_ratios': None}  #branching_ratios =  np.array([0.359, 0.856, 0.620])
    detector_geom = {'area_m2': 0.00196, 'distance_m': 0.10}
    
    results = compute_efficiencies(
        energies=energies,
        count_rates=count_rates,
        source_info=source_info,
        detector_geom=detector_geom,
        angles_deg=[0, 15, 30, 45, 60],
        plot=True
    )
    
    print("\n" + "="*60)
    print(f"EFFICIENCY RESULTS FOR {detector} DETECTOR")
    print("="*60)
    print(f"\n{'Energy (keV)':<15} {'Count Rate':<15} {'Abs. Eff.':<15} {'Intr. Eff.':<15}")
    print("-"*60)
    for i, E in enumerate(results['energies_keV']):
        print(f"{E:<15.1f} {results['areas_counts_per_s'][i]:<15.1f} {results['absolute_efficiency'][i]:<15.6f} {results['intrinsic_efficiency'][i]:<15.6f}")


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='''This script will return csv files of results used 
    to characterize a detector based on given data files''')
    parser.add_argument('data', type = str, help = "csv of data from spectrum_reader", default = None)
    parser.add_argument('detector', type = str, help = "name of detector used", default = None)
    args = parser.parse_args()

    main(args.data, args.detector)

