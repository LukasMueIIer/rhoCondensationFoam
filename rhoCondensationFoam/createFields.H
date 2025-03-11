#include "createRDeltaT.H"

Info<< "Reading thermophysical properties\n" << endl;
autoPtr<rhoReactionThermo> pThermo(rhoReactionThermo::New(mesh));
rhoReactionThermo& thermo = pThermo();
thermo.validate(args.executable(), "h", "e");

basicSpecieMixture& composition = thermo.composition();
PtrList<volScalarField>& Y = composition.Y();

//Find the water field and give us seperate access
volScalarField* pYliquidH2O;
volScalarField* pYVapourH2O;

label idLiquidH2O = 999; //Identifier label for liquidH2O so we can addapt its transport equation
label idVapourH2O = 999;

forAll(Y, i)
{
    volScalarField& Yi = Y[i];
    if(Yi.name() == word("liquidH2O"))
    {
        Info << "Found liquid water phase " << endl;
        pYliquidH2O = &Yi;
        idLiquidH2O = i;
    }else if(Yi.name() == word("vapourH2O"))
    {
        Info << "Found vapour water phase " << endl;
        pYVapourH2O = &Yi;
        idVapourH2O = i;
    }
}
volScalarField& YLiquidH2O = *pYliquidH2O;
volScalarField& YVapourH2O = *pYVapourH2O;

            
const word inertSpecie(thermo.get<word>("inertSpecie"));
if (!composition.species().found(inertSpecie))
{
    FatalIOErrorIn(args.executable().c_str(), thermo)
        << "Inert specie " << inertSpecie << " not found in available species "
        << composition.species()
        << exit(FatalIOError);
}

volScalarField rho
(
    IOobject
    (
        "rho",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    thermo.rho()
);

volScalarField rhoVapour
(
    IOobject
    (
        "rhoVapour",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    thermo.rho()
);

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);


volScalarField& p = thermo.p();

#include "compressibleCreatePhi.H"

pressureControl pressureControl(p, rho, pimple.dict(), false);

mesh.setFluxRequired(p.name());


Info << "Creating turbulence model.\n" << nl;
autoPtr<compressible::turbulenceModel> turbulence
(
    compressible::turbulenceModel::New
    (
        rho,
        U,
        phi,
        thermo
    )
);

Info<< "Creating reaction model\n" << endl;
autoPtr<CombustionModel<rhoReactionThermo>> reaction
(
    CombustionModel<rhoReactionThermo>::New(thermo, turbulence())
);

multivariateSurfaceInterpolationScheme<scalar>::fieldTable fields;

forAll(Y, i)
{
    fields.add(Y[i]);
}
fields.add(thermo.he());


volScalarField Qdot
(
    IOobject
    (
        "Qdot",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimEnergy/dimVolume/dimTime, Zero)
);

#include "createDpdt.H"

#include "createK.H"

#include "createMRF.H"

const dimensionedScalar rhoMax("rhoMax", dimDensity, GREAT, pimple.dict());
const dimensionedScalar rhoMin("rhoMin", dimDensity, Zero, pimple.dict());

#include "createFvOptions.H"

//Create Custom Fields

volScalarField pVapourH2O //Partial pressure of the water vapour phase
(
    IOobject
    (
        "pVapourH2O",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimPressure, Zero)
);

volScalarField pSaturationLiquidH2O //Local saturation Pressure wrt. Water
(
    IOobject
    (
        "pSaturationLiquidH2O",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimPressure, Zero)
);

volScalarField SaturationLiquidH2O //Local saturation Pressure wrt. Water
(
    IOobject
    (
        "SaturationLiquidH2O",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimless, Zero)
);

