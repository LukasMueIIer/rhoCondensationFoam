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

#custom functions

def PostProcessing(dir_path,samp_dT,u,d):    
    #dir_path is the path of the directory in which simulation will be done
    if not os.path.isdir(dir_path):
        print("Passed working directory path is NOT valid!")
        return 1

    #case specific code
    Ui = 10
    Ua = 5
    Ti = 500
    Ta = 298

    #Load the File from the exported Paraview File and Plot
    # File path (update this with the actual file path)

    ParaFiles = ["/plot_LRR.csv","/SST_ParaView.csv"]

    def plot_from_paraview(filePath):
        # Load the data into a DataFrame
        # Since your data includes mixed formatting, you may need to explicitly handle special characters or delimiters.
        data = pd.read_csv(dir_path + filePath)

        # Extract the desired columns
        u_columns = ["U:0", "U:1", "U:2"]
        points_column = ["Points:0"]  # Adjust this name if it's not exactly as shown
        t_column = "T"  # Temperature column

        # Check if columns exist in the file
        if all(col in data.columns for col in u_columns) and points_column[0] in data.columns:
            # Combine U columns into a single array
            u_array = data[u_columns].to_numpy()

            # Extract Points:0 as an array
            points_array = data[points_column[0]].to_numpy()

            t_values = data[t_column].to_numpy()

            print("U array:")
            print(u_array)

            print("\nPoints array:")
            print(points_array)
        else:
            print("One or more specified columns are missing from the file.")
        #Ti = np.max(t_values)
        dU = Ui - Ua
        dT = Ti - Ta
        
        Uc = u_array[:, 0]
        Uc_normed = (Uc - Ua) / dU

        Tc_normed = (t_values - Ta) / dT

        # Plot (U_0 - 5) vs Points:0
        plt.figure(figsize=(8, 6))
        plt.plot(points_array, Uc_normed, color = "green", label = "delt U / delt U0")
        plt.plot(points_array, Tc_normed, color = "red", label = "delt T / delt T0")
        plt.xlabel('x [m]')
        plt.ylabel('$delta  / delta 0$')
        plt.legend()
        plt.grid(True)

        input_string = filePath
        input_string = input_string.lstrip('/')

        # Split by the first dot and take the part before it
        extracted_name = input_string.split('.')[0]
        plt.title(extracted_name)
        plt.savefig(extracted_name + ".png")  # Save as a PNG file

    for file in ParaFiles:
        plot_from_paraview(file)

    return 0 #return 0 if ran sucessfully


#independent run
if __name__ == "__main__":
    print("PostProcessing running as standalone")

    #get working directory
    dir_path = general.get_start_path()
    pp_state = PostProcessing(dir_path,samp_dT = 0.025,u = 0.15, d = 0.1)
    if(pp_state == 0):
        print("PostProcessing done sucessfully!")
    else:
        print("An Error occured with code: " + str(pp_state))
