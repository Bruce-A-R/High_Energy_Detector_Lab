import numpy as np 
import matplotlib.py as plt

def calculate_geometric_factor(detector_area, distance, angle_deg = 0.0):

  # caculate geometric factor G = A_proj / (4pi d ** 2)

  angle_rad = np.deg2rad(angle_deg)
  A_proj = detector_area * np.pi * distance**2
  G = A_proj / (4.0 * np.pi * distance**2)
  return G

def calculate_efficiencies(count_rates, count_errors, activity, branching_ratio, geometric_factor):

    # calculate absolute and intrinsic efficiencies.

    photon_emission_rate = activity * branching_ratios

    # Absolute efficiency
    abs_eff = count_rates / photon_emission_rate
    abs_eff_err = abs_eff_err / photon_emission_rate

    # Intrinsic efficiency
    intr_eff = abs_eff / geometric_factor
    intr_eff_err = intr_eff_err / geometric_factor

    return {
        'absolute': abs_eff,
        'absolute_err': abs_eff_err,
        'intrinsic': intr_eff,
        'intrinsic_err': intr_eff_err
    }


def fit_and_evaluate_efficiency(energies, efficiencies, evaluated_energy = None):
  
  # Fit ln(ε) = a + b·ln(E) + c·(ln(E))²  

  ln_E = np.log(energies)
  ln_eff = np.log(efficiencies)
  coeffs = np.polyfit(ln_E, ln_eff, 2)

  #  Evaluate fitted efficiency model.
  if evaluated_energy is  None:
    evaluated_energy = energies

  ln_E_eval = np.log(evaluated_energy)
  ln_eff_eval = np.polyval(coeffs, ln_E_eval)
  fitted_eff = np.exp(ln_eff_eval)

  return fitted_eff, coeffs


def plot_efficiency(energies, efficiencies, errors = None, fit_coeffs = None, ylable = 'Efficiency', title = 'Efficiency vs Energy'):

  # Plotting efficiency vs energy on log scale.
  fig, ax = plt.subplots(fisize = (8, 6))

# Plot data
if errors is not None:
  ax.errorbar(energies, efficiencies, yerr = errors, fmt = 'o', markersize = 5, capsizer = 3, lable = 'Data')

else:
  ax.plot(energies, efficiencies, 'o', markersize = 5, label = 'Data')

# Plot fit
if fit_coeffs is not None:
        E_fit = np.logspace(np.log10(energies.min()*0.9), 
                           np.log10(energies.max()*1.1), 200)
        eff_fit = evaluate_fit(E_fit, fit_coeffs)
        
        c, b, a = fit_coeffs
        label = f'Fit: ln(ε) = {a:.3f} + {b:.3f}·ln(E) + {c:.3f}·(ln(E))²'
        ax.plot(E_fit, eff_fit, '-r', linewidth=2, label=label)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Energy (keV)', fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3, which='both')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.show()


def plot_angular_dependence(angles, efficiencies, ylable = 'Intrinsic Efficiency', title = 'Efficiency vs Angle'):

  # Plot efficiency vs angle
  fig, ax = plt.subplots(figsize=(8, 5))
  ax.plot(angles, efficiencies, 'o-', markersize=8, linewidth=2)
  ax.set_xlabel('Angle (deg)', fontsize=12)
  ax.set_ylabel(ylabel, fontsize=12)
  ax.set_title(title, fontsize=14, fontweight='bold')
  ax.grid(alpha=0.3)
  plt.tight_layout()
  plt.show()


def analyze_detector_efficiency(energies, count_rates, count_errors, activity, branching_ratios, detector_area, distance, angles_deg=None, plot_results=True):
  
   # Complete efficiency analysis pipeline.
   # Convert inputs to arrays
  energies = np.asarray(energies)
  count_rates = np.asarray(count_rates)
  count_errors = np.asarray(count_errors)

  # Handle branching ratios
  if np.isscalar(branching_ratios):
      branching_ratios = np.full_like(energies, branching_ratios)
  else:
      branching_ratios = np.asarray(branching_ratios)

  # Calculate geometric factor at 0 degrees
  G = calculate_geometric_factor(detector_area, distance, angle_deg=0.0)

  # Calculate efficiencies
  eff = calculate_efficiencies(count_rates, count_errors, activity, 
                                branching_ratios, G)

  # Fit intrinsic efficiency model
  fit_coeffs = fit_efficiency_model(energies, eff['intrinsic'])

  # Print results
  print("="*60)
  print("EFFICIENCY ANALYSIS RESULTS")
  print("="*60)
  print(f"\nGeometric factor G = {G:.6e}")
  print(f"\nFit parameters [ln(ε) = a + b·ln(E) + c·(ln(E))²]:")
  print(f"  a = {fit_coeffs[2]:.4f}")
  print(f"  b = {fit_coeffs[1]:.4f}")
  print(f"  c = {fit_coeffs[0]:.4f}")

  print(f"\n{'Energy (keV)':<15} {'Abs. Eff.':<15} {'Intr. Eff.':<15}")
  print("-"*45)
  for i in range(len(energies)):
      print(f"{energies[i]:<15.1f} {eff['absolute'][i]:<15.6f} {eff['intrinsic'][i]:<15.6f}")

  # Generate plots
  if plot_results:
      # Absolute efficiency plot
      plot_efficiency(energies, eff['absolute'], eff['absolute_err'],
                      ylabel='Absolute Efficiency', 
                      title='Absolute Efficiency vs Energy')
      
      # Intrinsic efficiency plot with fit
      plot_efficiency(energies, eff['intrinsic'], eff['intrinsic_err'],
                      fit_coeffs=fit_coeffs,
                      ylabel='Intrinsic Efficiency',
                      title='Intrinsic Efficiency vs Energy')
      
      # Angular dependence (if angles provided)
      if angles_deg is not None and len(angles_deg) > 1:
          angles_deg = np.asarray(angles_deg)
          # Use strongest peak for angular analysis
          strongest_idx = np.argmax(count_rates)
          
          eff_angles = []
          for angle in angles_deg:
              G_angle = calculate_geometric_factor(detector_area, distance, angle)
              eff_dict = calculate_efficiencies(
                  count_rates[strongest_idx:strongest_idx+1],
                  count_errors[strongest_idx:strongest_idx+1],
                  activity,
                  branching_ratios[strongest_idx:strongest_idx+1],
                  G_angle
              )
              eff_angles.append(eff_dict['intrinsic'][0])
          
          plot_angular_dependence(angles_deg, np.array(eff_angles),
                                title=f'Efficiency vs Angle ({energies[strongest_idx]:.1f} keV)')

  # Return results
  results = {
      'energies': energies,
      'count_rates': count_rates,
      'count_errors': count_errors,
      'branching_ratios': branching_ratios,
      'geometric_factor': G,
      'absolute_efficiency': eff['absolute'],
      'absolute_efficiency_err': eff['absolute_err'],
      'intrinsic_efficiency': eff['intrinsic'],
      'intrinsic_efficiency_err': eff['intrinsic_err'],
      'fit_coefficients': fit_coeffs
  }

  return results
