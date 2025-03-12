//Equations related to saturation, partial Pressure condensation etc.

//Hardcoded Values (for ease of implementation)

dimensionedScalar RVapourH2O("RVapourH2O",dimGasConstant,461.4);

//calculate partial pressure of water
Info << "Calculating water vapour partial pressure " << nl <<endl;

pVapourH2O = rho * YVapourH2O * RVapourH2O * T;

Info << "Calculating local water vapour density" << nl << endl;

rhoVapour = rho * YVapourH2O; 

//Calculate saturation pressure
Info << "Updating Saturation pressures " << nl << endl;

dimensionedScalar fracT("fractTvapour",dimTemperature,373.16); //A often used Temperature value for the calculation of saturation pressure
dimensionedScalar capPressure("saturationPressureCap",dimPressure,1e5); //Used to cap the saturation pressure

pSaturationLiquidH2O = 
pow(10, -7.90298*(fracT/T-1) 
+  5.02808 * log10(fracT/T)
- 1.3816e-7 * (pow(10,11.344*(1-T/fracT)) - 1)
+ 8.1328e-3 * (pow(10,-3.49149*(fracT/T-1) ) - 1) 
+ log10(dimensionedScalar(dimless,1013.246))) * dimensionedScalar("pressureFactor",dimPressure,100) 
* neg(T - fracT)
+ capPressure * pos(T - fracT);


Info << "Calculating Saturations " << nl << endl;

SaturationLiquidH2O = pVapourH2O / (pos(pSaturationLiquidH2O) * pSaturationLiquidH2O + dimensionedScalar(dimPressure,0.01)); //Make sure we never divide by 0