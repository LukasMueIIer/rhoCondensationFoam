##In this script all PostProcessing is done

#fixed imports
from FoamFunctions.Tools import general
from FoamFunctions.Tools import data_readers
from FoamFunctions.Tools import data_processing
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#custom imports
import itertools

#custom functions

def PostProcessing(dir_path):    
    #dir_path is the path of the directory in which simulation will be done
    if not os.path.isdir(dir_path):
        print("Passed working directory path is NOT valid!")
        return 1

    #case specific code
    Ui = 10
    Ua = 5
    Ti = 500
    Ta = 298

    csv_path = dir_path+"/postProcessing/customOutputFile.dat"

    csv = pd.read_csv(csv_path)

    plt.figure(figsize=(10, 6))
    plt.scatter(csv["T"], csv["pVapour"], marker='+', label='pVapour vs T')
    plt.scatter(csv["T"], csv["pSaturationWater"], marker='+', label='pSaturation')
    plt.xlabel("Temperature (T)")
    plt.ylabel("Vapour Pressure (pVapour)")
    plt.xlim(right=265,left=225)
    plt.ylim(top=400,bottom = 0)
    plt.legend()
    plt.grid(True)

    plt.savefig(dir_path+"/postProcessing/molierPlot.png")

    return 0 #return 0 if ran sucessfully


#independent run
if __name__ == "__main__":
    print("PostProcessing running as standalone")

    #get working directory
    dir_path = general.get_start_path()
    pp_state = PostProcessing(dir_path)
    if(pp_state == 0):
        print("PostProcessing done sucessfully!")
    else:
        print("An Error occured with code: " + str(pp_state))
