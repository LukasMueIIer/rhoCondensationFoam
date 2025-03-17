import PreProcessing
import Simulation
import PostProcessing
from FoamFunctions.Tools import general


pp_state = PreProcessing.PreProcessing(general.get_start_path())

if(pp_state == 0):
    print("PreProcessing done sucessfully!")
else:
    print("An Error occured with code: " + str(pp_state))


sim_state = Simulation.Simulation(general.get_start_path())
if(sim_state == 0):
    print("Simulation done sucessfully!")
else:
    print("An Error occured with code: " + str(sim_state))


#skipping postProcessing for now
#post_state = PostProcessing.PostProcessing(general.get_start_path(),0.025,u,d)
#if(sim_state == 0):
#    print("PostProcessing done sucessfully!")
#else:
#    print("An Error occured with code: " + str(sim_state))
