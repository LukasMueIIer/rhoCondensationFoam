# rhoCondensationFoam
A derivative of rhoReactingFoam, with the goal of simulating particle loaded flows with condensation (and maybe icing).

## Examples
Contains some test cases for the solver. All is based on a python workflow for automated simulation execution.
Requires a python environment with:
PyFoam
Classy_Blocks
FoamFunctions

## Equation of State
We face one problem. Air and water vapour are compressible, condensed water and ice are not. Now based on my current understanding
of the FOAM source code a ton of could would have to be rewritten to implement this "naturally".
Therefore we will default to using polynomial EOS, which in the case of Ideal Gas and a incompressible liquid 
should be no problem.

## Supported Versions:
v2406 - Development Base

other versions might work too, tell me if you test it succesfully