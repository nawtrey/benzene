# Support function for molecular dynamics of benzene
# Functions for setting up the system
#
# Written by Nikolaus Awtrey, Justin Gens, and Ricky for ASU PHY494
# http://asu-compmethodsphysics-phy494.github.io/ASU-PHY494/

#========================================================
# Uses SI units everywhere
#========================================================

import numpy as np

kB = 1.3806488e-23     # J/K; Bolzmann's constant
eps = 1.654e-30/kB  # Kelvin
sigma = 0.341           # nm

#========================================================
#============= Functions ================================
#========================================================

def random_direction(N):
    """
    Takes a number of particles to create an array of random momenta

    Parameters
    ----------
    N : integer
        Number of atoms in the system

    Returns
    -------
    Velocities : array
        (Nx3) array of random velocities (Vx, Vy, Vz)
    """
    rand_dir = np.random.rand(N, 3) - 0.5
    normalized = [i/np.linalg.norm(i) for i in rand_dir]
    return normalized


def instantaneous_temperature(vels, masses):
    """
    Calculates the instantaneous temperature of the system for a single time step

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    masses : array
        (Nx1) array of all atom masses in system

    Returns
    -------
    Temperature : float
        Value of system temperature in Kelvin

    """
    N = len(vels)
    Nf = 3*N - 6
    return np.sum(vels**2, axis=1) * masses / kB*Nf

def kinetic_temperature(vels):
    """
    Calculates the kinetic temperature of the molecule
    --------------------------------------------------
    Note: PBC simulations Nf = 3N - 3  (translation)
          droplet in vacuo: Nf = 3N - 6 (translation and rotation)
          droplet with external spherical boundary potential: Nf = 3N-3 (rotation)

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    masses : array
        (Nx1) array of all atom masses in system

    Returns
    -------
    Kinetic Temperature : float
    """
    N = len(vels)
    Nf = 3*N - 6
    return np.sum(vels**2)/kB*Nf

def average_system_momentum(vels):
    """Caclulates average system momentum at a specific time step."""
	#####NEED TO DO WITH CORRECT MASS
    return np.mean(vels, axis=0)

def remove_linear_momentum(moms):
    """
    Removes linear momentum of entire system of atoms

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    masses : array
        (Nx1) array of all atom masses in system

    Returns
    -------
    Velocities : array
        (Nx3) array of new velocities (Vx, Vy, Vz)
    """
    return moms - np.mean(moms, axis=0)

def rescale(vels, temperature):
    """
    Rescale velocities so that they correspond to temperature T.

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    temperature : float
        Value of initial system temperature in Kelvin

    Returns
    -------
    Velocities : array
        (Nx3) array of rescaled velocities (Vx, Vy, Vz)

    """
    current_temperature = kinetic_temperature(vels)
    return np.sqrt(temperature/current_temperature) * vels

def total_momentum(vels, masses):
    """
    Calculates the total linear momentum of the system of atoms

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    masses : array
        (Nx1) array of all atom masses in system

    Returns
    -------
    Momentum : float
        Magnitude of the total linear momentum of the system |P|
    """
    return np.sum(vels*masses, axis=0)

def KE(vels, masses):
    """
    Calculates the kinetic energy of a single particle for a single time step

    Parameters
    ----------
    vels : array
        (Nx3) array of velocities for every atom in system
    masses : array
        (Nx1) array of all atom masses in system

    Returns
    -------
    Kinetic Energy : float
    """
    return 0.5*masses*np.sum(vels**2, axis = 1)

def F_LJ(r):
    """
    Lennard-Jones force magnitude
    """
    return 4*eps*(6/r*(sigma/r)**12 - 12/r*(sigma/r)**6)

def V_LJ(positions):
    """
    Calculates the potential energy due to the LJ potential
    between a pair of atoms for a single time step

    Parameters
    ----------
    positions : array
        (Nx3) array of positions for every atom in system

    Returns
    -------
    Potential Energy : float
    """
    r_mag = np.sqrt(np.sum(positions*positions))      # Calculates the magnitude of r_vector
    if r_mag == 0.0:
        return 0
    else:
        return 4*eps*((sigma/r_mag)**12 - (sigma/r_mag**6))

def V_M(r,bond):
    """
    Calculates the potential energy due to the Morse potential
    between a pair of atoms for a single time step

    Parameters
    ----------
    D_e     : well depth
    r       : distance between atoms
    r_e     : equilibrium bond distance
    beta    : controls 'width' of the potential
    k_e     : force constant at the minimum of the well

    Returns
    -------
    Potential Energy : float
    """
    params = {'CC':{'r_e': 0.139, 'D_e': 5000.0000,'k_e': 2*3924952},
              'CH':{'r_e': 0.109, 'D_e': 1472.3736,'k_e': 3924952},
              'HC':{'r_e': 0.109, 'D_e': 1472.3736,'k_e': 3924952}}
    values = params[bond]
    k_e = values['k_e']
    D_e = values['D_e']
    r_e = values['r_e']
    r2 = r - r_e
    beta = np.sqrt(k_e/(2*D_e))
    return D_e*(1-np.exp(-beta*r2))**2 


def F_M(r,bond):
    """
    Calculates the potential energy due to the Morse potential
    between a pair of atoms for a single time step

    Parameters
    ----------
    D_e     : well depth
    r       : distance between atoms
    r_e     : equilibrium bond distance
    beta    : controls 'width' of the potential
    k_e     : force constant at the minimum of the well

    Returns
    -------
    Potential Energy : float
    """
    params = {'CC':{'r_e': 0.139, 'D_e': 922000,'k_e': 1.49017e6},
              'CH':{'r_e': 0.109, 'D_e': 110,'k_e': 9.685e5},
              'HC':{'r_e': 0.109, 'D_e': 110,'k_e': 9.685e5}}
    values = params[bond]
    k_e = values['k_e']
    D_e = values['D_e']
    r_e = values['r_e']
    r2 = r - r_e
    beta = np.sqrt(k_e/(2*D_e))
    return -2*beta*D_e*(np.exp(-2*beta*r2) - np.exp(-beta*r2))

#def DA(positions, i):
#    """
#    Calculates the dihedral angle
#
#    Paramaters
#    ----------
#    positions : array
#        (Nx3) array of positions for every atom in system
#    i : reference atom
#    """
#    r_ij = np.abs(positions[i] - positions[i+1])
#    r_jk = np.abs(positions[i] - positions[i+6])
#    r_lk = np.abs(positions[i+6] - positions[i+12])
#    a = np.cross(r_ij, r_jk)
#    b = np.cross(r_lk, r_jk)
#    costheta = np.dot(a,b) / np.linalg.norm(a*b)
#    theta = np.arccos(costheta)
#    return theta
#
#def V_D(positions, i):
#    """
#    Calculates the Dihedral Potential
#
#    Paramaters
#    ----------
#    positions : array
#        (Nx3) array of positions for every atom in system
#    i : reference atom
#    """
#    theta = DA(positions, i)
#
#    # "Cosine functional form"
#    theta_0 = np.pi*120/180  # angle where potential passes through its minimum value, reference dihedral angle
#    V_n = 10     # barrier height, "force constant"
#    n = 1    # multiplicity, "the number of minima as the bond is rotated through 360deg"
#    V_DA =  (V_n/2) * (1 + np.cos(n*theta - theta_0))  # dihedral angle potential - cosine form]
#
#    # "Harmonic form"
#    phi_0 =   # reference dihedral angle
#    k = 10  # force constant (different that cosine form force constant)
#    V_DH = k *(theta - phi_0)**2
#
#    return V_DH

def constraints(positions,data):
    """
    positions is an array of all positions
    """
    #bond lengths 
    rc = 0.139
    rh = 0.109
    
    #force constant
    kc = 100000000
    kh = 100000000000

    #define a plane based on carbons 1 3 5
    x_c = 1/3*(positions[0][0]+positions[2][0]+positions[4][0])
    y_c = 1/3*(positions[0][1]+positions[2][1]+positions[4][1])
    z_c = 1/3*(positions[0][2]+positions[2][2]+positions[4][2])

    #center of molecule
    center = np.array([x_c,y_c,z_c])

    #normal vector
    normal = np.cross(positions[2]-positions[0],positions[4]-positions[0])
    normal = normal/np.linalg.norm(normal)

    #vectors to all atoms from center
    rvecs = [positions[i]-center for i in range(12)]

    #vectors to equilibrium positions of hydrogens
    eq_vecs = np.array([[0.139, 0.   , 0.   ],                              
    [0.0695    , 0.12037753, 0.        ],               
    [-0.0695    ,  0.12037753,  0.        ],            
    [-1.38999999e-01,  1.70225912e-17,  0.00000000e+00],
    [-0.0695    , -0.12037753,  0.        ],            
    [ 0.0695    , -0.12037753,  0.        ],            
    [0.248, 0.   , 0.   ],                              
    [0.124    , 0.2147743, 0.       ],                  
    [-0.124    ,  0.2147743,  0.       ],               
    [-2.47999996e-01,  3.03712398e-17,  0.00000000e+00],
    [-0.124    , -0.2147743,  0.       ],               
    [ 0.124    , -0.2147743,  0.       ]])               

    forces = np.zeros((12,3))
    forces = [[(eq_vecs[i][0]-rvecs[i][0])/data[i][3],(eq_vecs[i][1]-rvecs[i][1])/data[i][3],(eq_vecs[i][2]-rvecs[i][2])/data[i][3]] for i in range(len(rvecs))]
    forces[:6] = np.multiply(forces[:6],kc)
    forces[6:] = np.multiply(forces[6:],kh)
    return forces
    
def cutoff_r(pos_array,cutoff):
    for i in range(len(pos_array)):
        for j in range(len(pos_array[0])):
            if pos_array[i,j]>cutoff:
                pos_array[i,j]=0
    return pos_array
