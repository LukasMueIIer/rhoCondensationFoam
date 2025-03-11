## In this script the simulation is executed

#fixed imports
from FoamFunctions.Tools import general
from FoamFunctions.Solvers import Sim_Master
import os
import shutil

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

#custom imports
from PyFoam.Execution.ParallelExecution import LAMMachine
#custom functions

def Simulation(dir_path):
    #dir_path is the path of the directory in which simulation will be done
    if not os.path.isdir(dir_path):
        print("Passed working directory path is NOT valid!")
        return 1
  
    sim_master = Sim_Master.sim_master(dir_path,4)  #general sim_master which is used to execute simulations

    #case specific code

    #run steady state simulation
    sf_sim = Sim_Master.sim_step(solver="rhoCondensationFoam",silent=False)
    sf_sim.time = 10    #simulate 10 steps
    sf_sim.dT = 0.001
    sf_sim.writeInterval = 0.1    #write every step
    sf_sim.ddTSchemes = "Euler"

    #set Turbulence Model
    turb = ParsedParameterFile(dire.constantDir() + "/turbulenceProperties")
    turb["RAS"]["RASModel"] = "kOmegaSST"
    turb.writeFile()

    sim_master.execute(sf_sim)  #run the simulation

    def remove_turbulence_properties_prefix(directory_path):
        """
        For every file in `directory_path` that starts with 'turbulenceProperties:',
        remove that exact prefix from the file name.
        """
        prefix = "turbulenceProperties:"
        for filename in os.listdir(directory_path):
            old_path = os.path.join(directory_path, filename)

            # Only proceed if it's a file (not a directory) and starts with the prefix
            if os.path.isfile(old_path) and filename.startswith(prefix):
                new_filename = filename[len(prefix):]  # Remove the prefix
                new_path = os.path.join(directory_path, new_filename)
                os.rename(old_path, new_path)

    
    general.reconstruct(dir_path) #reconstruct case

    dire = SolutionDirectory(dir_path)

    ##Adapt the R and K File
    remove_turbulence_properties_prefix(dire.latestDir())
    og0_file = dir_path + "/0.org"
    init_par_R_file = ParsedParameterFile(og0_file + "/R")
    par_R_file = ParsedParameterFile(dire.latestDir() + "/R")
    par_R_file["boundaryField"] = init_par_R_file["boundaryField"]
    
    par_R_file.writeFile()
    
    init_par_R_file = ParsedParameterFile(og0_file + "/epsilon")
    par_R_file = ParsedParameterFile(dire.latestDir() + "/epsilon")
    par_R_file["boundaryField"] = init_par_R_file["boundaryField"]
    
    par_R_file.writeFile()
    
    #Remove all Processor Directories, and decompose again
    def delete_processor_folders(directory_path):
        """
        Deletes all folders that start with "processor" in the specified directory.

        Parameters:
            directory_path (str): Path to the directory where folders will be deleted.

        Returns:
            None
        """
        try:
            # Check if the provided directory path exists
            if not os.path.exists(directory_path):
                print(f"The directory {directory_path} does not exist.")
                return

            # Iterate through items in the directory
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)

                # Check if the item is a folder and starts with "processor"
                if os.path.isdir(item_path) and item.startswith("processor"):
                    print(f"Deleting folder: {item_path}")
                    shutil.rmtree(item_path)  # Delete the folder and its contents

            print("Completed deletion of processor folders.")

        except Exception as e:
            print(f"An error occurred: {e}")

    delete_processor_folders(dir_path)
    
    general.decompose(dir_path,4,silent=False)

    #addapt turbulence model and relaxation
    #set Relaxation
    dire = SolutionDirectory(dir_path)
    fv_Schemes = ParsedParameterFile(dire.systemDir() + "/fvSolution")
    fv_Schemes["relaxationFactors"]["equations"]["\"(k|epsilon|omega|R)\""] = "0.3"
    fv_Schemes.writeFile()

    #set Turbulence Model
    turb = ParsedParameterFile(dire.constantDir() + "/turbulenceProperties")
    turb["RAS"]["RASModel"] = "LRR"
    turb.writeFile()

    #run solver agian
    sf_sim = Sim_Master.sim_step(solver="rhoSimpleCondensationFoam",silent=False)
    sf_sim.time = 10    #simulate 10 steps
    sf_sim.dT = 0.001
    sf_sim.writeInterval = 0.1    #write every step
    sf_sim.ddTSchemes = "Euler"

    sim_master.execute(sf_sim)  #run the simulation


    #set Turbulence Model
    turb = ParsedParameterFile(dire.constantDir() + "/turbulenceProperties")
    turb["RAS"]["RASModel"] = "SSG"
    turb.writeFile()

    #run solver agian
    sf_sim = Sim_Master.sim_step(solver="rhoSimpleCondensationFoam",silent=False)
    sf_sim.time = 10    #simulate 10 steps
    sf_sim.dT = 0.001
    sf_sim.writeInterval = 0.1    #write every step
    sf_sim.ddTSchemes = "Euler"

    sim_master.execute(sf_sim)  #run the simulation


    general.reconstruct(dir_path) #reconstruct case
    general.paraFoam(dir_path) #create paraFoam file

    return 0 #return 0 if ran sucessfully


#independent run
if __name__ == "__main__":
    print("Simulation running as standalone")

    #get working directory
    dir_path = general.get_start_path()
    sim_state = Simulation(dir_path)
    if(sim_state == 0):
        print("Simulation done sucessfully!")
    else:
        print("An Error occured with code: " + str(sim_state))