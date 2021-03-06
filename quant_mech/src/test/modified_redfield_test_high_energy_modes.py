'''
Created on 21 Nov 2014

Module to test modified Redfield code from open_systems module. Attempts to reproduce parts of figure 3 from Physical Origins and Models of Energy
Transfer in Photosynthetic Light-Harvesting by Novoderezhkin and van Grondelle (2010)

@author: rstones
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import quant_mech.utils as utils
import quant_mech.open_systems as os

def hamiltonian(delta_E, V):
    return np.array([[delta_E/2., V],
                    [V, -delta_E/2.]])

'''
Taken from Table 1 in Energy-Transfer Dynamics in the LHCII Complex of Higher Plants: Modified Redfield
Approach by Novoderezhkin, Palacios, van Amerongen and van Grondelle, J. Phys. Chem. B 2004 
'''
def LHCII_mode_params(damping):
        # freq and damping constant in wavenumbers
        return np.array([(97.,0.02396,damping),
                         (138.,0.02881,damping),
                         (213.,0.03002,damping),
                         (260.,0.02669,damping),
                         (298.,0.02669,damping),
                         (342.,0.06035,damping),
                         (388.,0.02487,damping),
                         (425.,0.01486,damping),
                         (518.,0.03942,damping),
                         (546.,0.00269,damping),
                         (573.,0.00849,damping),
                         (585.,0.00303,damping),
                         (604.,0.00194,damping),
                         (700.,0.00197,damping),
                         (722.,0.00394,damping),
                         (742.,0.03942,damping),
                         (752.,0.02578,damping),
                         (795.,0.00485,damping),
                         (916.,0.02123,damping),
                         (986.,0.01031,damping),
                         (995.,0.02274,damping),
                         (1052.,0.01213,damping),
                         (1069.,0.00636,damping),
                         (1110.,0.01122,damping),
                         (1143.,0.04094,damping),
                         (1181.,0.01759,damping),
                         (1190.,0.00667,damping),
                         (1208.,0.01850,damping),
                         (1216.,0.01759,damping),
                         (1235.,0.00697,damping),
                         (1252.,0.00636,damping),
                         (1260.,0.00636,damping),
                         (1286.,0.00454,damping),
                         (1304.,0.00576,damping),
                         (1322.,0.03032,damping),
                         (1338.,0.00394,damping),
                         (1354.,0.00576,damping),
                         (1382.,0.00667,damping),
                         (1439.,0.00667,damping),
                         (1487.,0.00788,damping),
                         (1524.,0.00636,damping),
                         (1537.,0.02183,damping),
                         (1553.,0.00909,damping),
                         (1573.,0.00454,damping),
                         (1580.,0.00454,damping),
                         (1612.,0.00454,damping),
                         (1645.,0.00363,damping),
                         (1673.,0.00097,damping)])
        
delta_E_values = np.linspace(0,2000,50) # wavenumbers
coupling_values = np.array([225., 100., 55.]) # wavenumbers
temperature = 77. # Kelvin
site_reorg_energy = 37. # wavenumbers
cutoff_freq = 30.
mode_damping = 3.
mode_params = LHCII_mode_params(mode_damping)

# rates, integrands, time = os.MRT_rate_ed(hamiltonian(10., 255.), reorg_energy, cutoff_freq, temperature, LHCII_mode_params(mode_damping), 20, 40.)
# plt.plot(time, integrands[0,1])
# plt.show()

# calculate line broadening functions etc...
time_interval = 10
time = np.linspace(0, time_interval, 32000.*time_interval)
num_expansion_terms = 20
g_site, g_site_dot, g_site_dot_dot, total_site_reorg_energy = os.modified_redfield_params(time, site_reorg_energy, cutoff_freq, temperature, mode_params, num_expansion_terms)
total_site_reorg_energies = np.array([total_site_reorg_energy, total_site_reorg_energy])
rates_data = []
   
print 'Calculating rates with high energy modes....'
for V in coupling_values:
    print 'Calculating rates for coupling ' + str(V)
    rates = []
    for i,delta_E in enumerate(delta_E_values):
        site_hamiltonian = hamiltonian(delta_E, V) + np.diag(total_site_reorg_energies) # adjust site energies by reorganisation shift
        evals, evecs = utils.sorted_eig(site_hamiltonian)
        # calculate exciton reorganisation energies
        exciton_reorg_energies = np.array([os.exciton_reorg_energy(evecs[i], total_site_reorg_energies) for i in range(site_hamiltonian.shape[0])])
        print exciton_reorg_energies
        evals = evals - exciton_reorg_energies # adjust to bare exciton reorganisation energies
        MRT = os.modified_redfield_rates(evals, evecs, g_site, g_site_dot, g_site_dot_dot, total_site_reorg_energy, temperature, time)
        rates.append(MRT[0,1])
    rates_data.append(rates)
      
#np.savez('../../data/modified_redfield_test_high_energy_modes_data.npz', delta_E_values=delta_E_values, coupling_values=coupling_values, rates=rates_data)
for i,rates in enumerate(rates_data):
    plt.subplot(1,3,i+1)
    plt.plot(delta_E_values, utils.WAVENUMS_TO_INVERSE_PS*np.array(rates))
plt.show()

# data = np.load('../../data/modified_redfield_test_high_energy_modes_data.npz')
# rates = data['rates']
# delta_E_values = data['delta_E_values']
# plt.plot(delta_E_values, -utils.WAVENUMS_TO_INVERSE_PS* rates)
# plt.show()