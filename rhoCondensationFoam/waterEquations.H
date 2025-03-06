//Equations related to saturation, partial Pressure condensation etc.

//Hardcoded Values (for ease of implementation)

dimensionedScalar RVapourH2O("RVapourH2O",dimGasConstant,461.4);



//calculate partial pressure of water
Info << "Calculating water partial pressure " << endl;

pVapourH2O = rho * YLiquidH2O * RVapourH2O * T;