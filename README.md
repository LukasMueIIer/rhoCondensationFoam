# rhoCondensationFoam
A derivative of rhoReactingFoam, with the goal of simulating particle loaded flows with condensation (and maybe icing).

## Assumptions
For now the goal is to keep the model very simple so the following simplifications are made:
1. The particles do not interact with each other (low particle density)
2. The Influence of the particles on turbulence is neglected (could be handled by adding a source term to the turbulence equations)
3. The Particles share the same velocity as the flow (assumes small stokes number)

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