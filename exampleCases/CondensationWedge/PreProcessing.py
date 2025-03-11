#fixed imports
from FoamFunctions.Tools import general
import os

#custom imports
from FoamFunctions.Tools import fluid_calcs
from FoamFunctions.Meshes import coax_jet
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import numpy as np
import math

#custom functions
import time

def PreProcessing(dir_path):    
    #dir_path is the path of the directory in which simulation will be done
    if not os.path.isdir(dir_path):
        print("Passed working directory path is NOT valid!")
        return 1

    ###case specific code

    ##clear up, remove parallel and postProcessing directories as well
    general.clean_parallel_and_postProcessing(dir_path)

    ##remove old pyfoam logs to prevent flodding
    general.remove_PyFoam_Logs(dir_path)

    #Delete all timesteps
    general.delete_time_folders(dir_path)

    ### Copy from OG
    general.copy_field_files(dir_path + "/0",dir_path + "/0.org",["p","T","U","omega","k","nut","alphat","epsilon","R","air","vapourH2O","liquidH2O"])


    ##create mesh
    #geometry
    ri = 0.03    #nozel radius
    ra = 2      #Outer radius
    l = 5      #length
    pipe_lengt = 1 #length of the virtual pipe
    alpha = 1   #spread angle
    x_chop = 100     #chopping amount in x-direction
    y_chop = 10       #chopping amount in y direction of the inlet 
    exp_Inlet = 1.05
    exp_Farfield = 1.05
    x_decay = 1.01

    coax_jet.piped_double_stacked_wedge_mesh(dir_path,ri,ra,l,pipe_lengt,alpha,x_chop,y_chop,exp_Inlet,exp_Farfield,x_decay)   #running classy blocks with modified mesh

    #execute blockMesh  
    general.run_Blockmesh(dir_path,silent=False)

    #setting up boundary conditions
    dire = SolutionDirectory(dir_path)

    ## Flow Conditions
    U9 = 10 #velocity in m/s
    U0 = 5  #velocity outside Flow
    I = 0.05 #turbulent Intensity
    T9 = 500 #Jet temperature in Kelvin
    T0 = 223.25 #Surrounding temperature
    p0 = 26499.9 #Pressure

    #velocity field
    par_u_file = ParsedParameterFile(dire.initialDir() + "/U")  #use paramter file access for this special BC
 
    par_u_file["boundaryField"]["inlet_inner"]["type"] = "fixedValue"
    par_u_file["boundaryField"]["inlet_inner"]["value"] = "uniform (%f 0 0)" %(U9)
 
    par_u_file["boundaryField"]["inlet_outer"]["type"] = "fixedValue"
    par_u_file["boundaryField"]["inlet_outer"]["value"] = "uniform (%f 0 0)" %(U0)

    par_u_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_u_file["boundaryField"]["upper"]["inletValue"] = "uniform (%f 0 0)" %(U0)
    par_u_file["boundaryField"]["upper"]["value"] = "uniform (%f 0 0)" %(U0)
 
    par_u_file["boundaryField"]["outlet"]["type"] = "zeroGradient"
 
    par_u_file["boundaryField"]["pipe"]["type"] = "noSlip"
 
    par_u_file["internalField"] = "uniform (%f 0 0)" %(U0)
    par_u_file.writeFile()

    #pressure field
    par_p_file = ParsedParameterFile(dire.initialDir() + "/p")

    par_p_file["boundaryField"]["inlet_inner"]["type"] = "zeroGradient"

    par_p_file["boundaryField"]["inlet_outer"]["type"] = "zeroGradient"

    par_p_file["boundaryField"]["upper"]["type"] = "outletInlet"
    par_p_file["boundaryField"]["upper"]["outletValue"] = "uniform %f" %(p0)
    par_p_file["boundaryField"]["upper"]["value"] = "uniform %f" %(p0)


    par_p_file["boundaryField"]["outlet"]["type"] = "fixedValue"
    par_p_file["boundaryField"]["outlet"]["value"] = "uniform %f" %(p0)

    par_p_file["boundaryField"]["pipe"]["type"] = "zeroGradient"

    par_p_file["internalField"] = "uniform %f" %(p0)
    
    par_p_file.writeFile()

    #Temperature field
    par_T_file = ParsedParameterFile(dire.initialDir() + "/T")

    par_T_file["boundaryField"]["inlet_inner"]["type"] = "fixedValue"
    par_T_file["boundaryField"]["inlet_inner"]["value"] = "uniform %f" %(T9)

    par_T_file["boundaryField"]["inlet_outer"]["type"] = "fixedValue"
    par_T_file["boundaryField"]["inlet_outer"]["value"] = "uniform %f" %(T0)

    par_T_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_T_file["boundaryField"]["upper"]["inletValue"] = "uniform %f" %(T0)
    par_T_file["boundaryField"]["upper"]["value"] = "uniform %f" %(T0)

    par_T_file["boundaryField"]["outlet"]["type"] = "zeroGradient"

    par_T_file["boundaryField"]["pipe"]["type"] = "zeroGradient"

    par_T_file["internalField"] = "uniform %f" %(T0)
    
    par_T_file.writeFile()

    #turbulent kin. energy
    par_k_file = ParsedParameterFile(dire.initialDir() + "/k")
    k0 = 3/2 * I**2 * U0**2 #initial guess for turbulent kin. energy
    k9 = 3/2 * I**2 * U9**2 #initial guess for turbulent kin. energy

    par_k_file["boundaryField"]["inlet_inner"]["type"] = "turbulentIntensityKineticEnergyInlet"
    par_k_file["boundaryField"]["inlet_inner"]["intensity"] = "%f" %(I)
    par_k_file["boundaryField"]["inlet_inner"]["value"] = "uniform %f" %(k9)

    par_k_file["boundaryField"]["inlet_outer"]["type"] = "inletOutlet"
    par_k_file["boundaryField"]["inlet_outer"]["inletValue"] = "uniform %f" %(k0)
    par_k_file["boundaryField"]["inlet_outer"]["value"] = "uniform %f" %(k0)

    par_k_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_k_file["boundaryField"]["upper"]["inletValue"] = "uniform %f" %(k0)
    par_k_file["boundaryField"]["upper"]["value"] = "uniform %f" %(k0)

    par_k_file["boundaryField"]["outlet"]["type"] = "inletOutlet"
    par_k_file["boundaryField"]["outlet"]["inletValue"] = "uniform %f" %(k0)
    par_k_file["boundaryField"]["outlet"]["value"] = "uniform %f" %(k0)

    par_k_file["boundaryField"]["pipe"]["type"] = "kqRWallFunction"
    par_k_file["boundaryField"]["pipe"]["value"] = "uniform %f" %(0)
    
    par_k_file["internalField"] = "uniform %f" %(k0)

    par_k_file.writeFile()

    #disipation rate epsilon
    l_turb = 0.07 * 2 * ri 
    l_turb_a = 0.07 * 2 * ra
    c = 0.09
    epsilon0 = (c**0.75 * k0 ** 1.5)/(l_turb_a)
    epsilon9 = (c**0.75 * k9 ** 1.5)/(l_turb)

    par_e_file = ParsedParameterFile(dire.initialDir() + "/epsilon")

    par_e_file["boundaryField"]["inlet_inner"]["type"] = "fixedValue"
    par_e_file["boundaryField"]["inlet_inner"]["value"] = "uniform %f" %(epsilon9)

    par_e_file["boundaryField"]["inlet_outer"]["type"] = "inletOutlet"
    par_e_file["boundaryField"]["inlet_outer"]["inletValue"] = "uniform %f" %(epsilon0)
    par_e_file["boundaryField"]["inlet_outer"]["value"] = "uniform %f" %(epsilon0)

    par_e_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_e_file["boundaryField"]["upper"]["inletValue"] = "uniform %f" %(epsilon0)
    par_e_file["boundaryField"]["upper"]["value"] = "uniform %f" %(epsilon0)

    par_e_file["boundaryField"]["outlet"]["type"] = "zeroGradient"

    par_e_file["boundaryField"]["pipe"]["type"] = "epsilonWallFunction"
    par_e_file["boundaryField"]["pipe"]["value"] = "uniform %f" %(0)

    par_e_file["internalField"] = "uniform %f" %(epsilon0)

    
    par_e_file.writeFile()

    par_R_file = ParsedParameterFile(dire.initialDir() + "/R")

    par_R_file["boundaryField"]["inlet_inner"]["type"] = "fixedValue"
    par_R_file["boundaryField"]["inlet_inner"]["value"] = "uniform (%f 0 0 %f 0 %f )" %(k9, k9 / 2, k9 / 2)

    par_R_file["boundaryField"]["inlet_outer"]["type"] = "inletOutlet"
    par_R_file["boundaryField"]["inlet_outer"]["inletValue"] = "uniform (%f 0 0 %f 0 %f )" %(k0, k0 / 2, k0 / 2)
    par_R_file["boundaryField"]["inlet_outer"]["value"] = "uniform (%f 0 0 %f 0 %f )" %(k0, k0 / 2, k0 / 2)

    par_R_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_R_file["boundaryField"]["upper"]["inletValue"] = "uniform (%f 0 0 %f 0 %f )" %(k0, k0 / 2, k0 / 2)
    par_R_file["boundaryField"]["upper"]["value"] = "uniform (%f 0 0 %f 0 %f )" %(k0, k0 / 2, k0 / 2)

    par_R_file["boundaryField"]["outlet"]["type"] = "zeroGradient"

    par_R_file["boundaryField"]["pipe"]["type"] = "kqRWallFunction"
    par_R_file["boundaryField"]["pipe"]["value"] = "uniform (0 0 0 0 0 0)"

    par_R_file["internalField"] = "uniform (%f 0 0 %f 0 %f )" %(k0, k0 / 2, k0 / 2)

    
    par_R_file.writeFile()


    #Write Omega File
    C_mu = 0.09
    w_0 = k0 ** 0.5 / ((C_mu**0.25) * pipe_lengt)
    w_9 = k9 ** 0.5 / ((C_mu**0.25) * ri)
    w_0 = w_9

    par_w_file = ParsedParameterFile(dire.initialDir() + "/omega")

    par_w_file["boundaryField"]["inlet_inner"]["type"] = "fixedValue"
    par_w_file["boundaryField"]["inlet_inner"]["value"] = "uniform %f" %w_9

    par_w_file["boundaryField"]["inlet_outer"]["type"] = "inletOutlet"
    par_w_file["boundaryField"]["inlet_outer"]["inletValue"] = "uniform %f" %w_0
    par_w_file["boundaryField"]["inlet_outer"]["value"] = "uniform %f" %w_0

    par_w_file["boundaryField"]["upper"]["type"] = "inletOutlet"
    par_w_file["boundaryField"]["upper"]["inletValue"] = "uniform %f" %w_0
    par_w_file["boundaryField"]["upper"]["value"] = "uniform %f" %w_0

    par_w_file["boundaryField"]["outlet"]["type"] = "zeroGradient"

    par_w_file["boundaryField"]["pipe"]["type"] = "omegaWallFunction"
    #["boundaryField"]["pipe"]["value"] = "uniform %f" %w_0

    par_w_file["internalField"] = "uniform %f" %w_0

    par_w_file.writeFile()

    #turbulent stress nut
    par_nut_file = ParsedParameterFile(dire.initialDir() + "/nut")

    par_nut_file["boundaryField"]["pipe"]["type"] = "nutkWallFunction"
    par_nut_file["boundaryField"]["pipe"]["value"] = "uniform 0"

    par_nut_file.writeFile()

    #copy 1 case and set initial field
    time.sleep(10)
    general.copy_and_renumber(dir_path,"0","1")
    general.run_setExprFields(dir_path)

    #renumber Mesh
    #general.renumber_Mesh(dir_path,silent=False) #renumbering must happen after setting the field
    
    #create paraView file
    general.paraFoam(dir_path,silent=False)

    #decompose
    general.decompose(dir_path,4,silent=False)

    return 0 #return 0 if ran sucessfully


#independent run
if __name__ == "__main__":
    print("PreProcessing running as standalone")

    #get working directory
    dir_path = general.get_start_path()



    pp_state = PreProcessing(dir_path)



    if(pp_state == 0):
        print("PreProcessing done sucessfully!")
    else:
        print("An Error occured with code: " + str(pp_state))
