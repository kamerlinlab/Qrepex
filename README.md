Qrepex 1.0
===========


#### Description
Q-RepEx is an open source tool designed to perform replica exchange
simulations with Q6. The idea is adapted from "H. Liu, A. Warshel, The catalytic effect of dihydrofolate reductase
and its mutants is determined by reorganization energies, Biochemistry
46 (20) (2007) 6011–6025. doi:10.1021/bi700201w". The procedure accelerates sampling by parallelising the FEP/US process and improves
statistics by increased sampling. The python script, Q-RepEx, main functionality is the unconditional exchange of simulation conditions for a series of
FEP/US simulations.


## System Requirements
 - Python 
 - git (optional)
 


# Installation

### External Executables:

Qrepex is relying on [**Q6**](https://doi.org/10.1016/j.softx.2017.12.001) which is free and opensource software licensed under the GPL v2.

- Q:  https://github.com/qusers/Q6

  Download and compile Q. Optionally install to $PATH.
  
### Download and Install Q-Repex:
We recommend using git to download Q-Repex, so that future releases of Q-Repex are easily accessible.

Here the suggested steps:



Clone into Q-Repex:
 
`git clone https://github.com/kamerlinlab/Qrepex qrepex`


## Workflow 
   The user provided input for Q-RepEx is purposely short in order to ease
functionality. An example input is shown below:

        python repex v1.X.py fep 10 5

repex v1.X.py is the name of the current version of Q-RepEx, fep is the
base filename, 10 is the number of US windows and 5 is the number of consecutive runs to be performed. The base filename has to be used for the input,
output, trajectory, restart and energy files. A help module is provided in
Q-RepEx. It can be activated by issuing:

        python repex v0.3.py help

## How to Cite this Work
The development of Q-RepEx is mainly funded by academic research grants. To help 
us fund development, we humbly ask that you cite the Q-RepEx paper:

* Q-RepEx: A python pipeline to increase sampling of
EVB simulations
  
