# Example Case Condensing Jet, Wedge
## Case
A hot jet of air is exhausted into a cold environment.

## Setup
### Mesh
We run a quasi 2D simulation based on the wedge boundary condition. The mesh is created with blockMesh

### Turbulence Modeling
We run multiple cascaded simulations with differing turbulence models:
1. SST Model
2. LRR RSM Model
3. SSG RSM Model
This is to validate that the solver works with all these models, as well as to show the different behaviour of these models
