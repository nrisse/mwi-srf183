"""
This script assures that the conversion from original SRF to linearized and
normalized is correct.
"""


import numpy as np


# db like original SRF measurement
x_db0 = np.array([-100, -100, -100, -100, -0.1, 0, -2, -3, -6, -21, -43, -1])

# linearized
x_lin = 10**(0.1*x_db0)

# linearized and normalized to unity
x_lino = x_lin/np.sum(x_lin)    

# converted back to dB
x_db = 10*np.log10(x_lino)

# normalized to maximum of 0
x_db0_ = x_db - np.max(x_db)
    
assert np.all(np.abs(x_db0 - x_db0_) < 1e-14)

# effect of perturbation
# does not matter if applied on the shifted dB values or normalized values
x_db_p = x_db.copy()
x_db0_p = x_db0.copy()

x_db_p[:6] += 2
x_db0_p[:6] += 2

# linearized
x_db_p_lin = 10**(0.1*x_db_p)
x_db0_p_lin = 10**(0.1*x_db0_p)

# linearized and normalized to unity
x_db_p_lino = x_db_p_lin/np.sum(x_db_p_lin)   
x_db0_p_lino = x_db0_p_lin/np.sum(x_db0_p_lin)   

assert np.all(np.abs(x_db_p_lino - x_db0_p_lino) < 1e-14)

x_db0_p_lino / x_lino
