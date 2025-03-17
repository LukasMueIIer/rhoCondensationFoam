#!/bin/bash

#SBATCH --job-name=openfoam_job       # Define the name of the job
#SBATCH --partition=doc  	      # Define the partition that should be used -> doc
#SBATCH --nodes=1                     # Define the number of nodes that should be assigned (servers)
#SBATCH --ntasks=40                   # Number of tasks (processors)
#SBATCH --ntasks-per-node=40          # Number of tasks per node
#SBATCH --time=24:00:00               # Runtime, max is 10 days
#SBATCH --output=slurm.%j.out         # Standard Output File
#SBATCH --error=slurm.%j.err          # Error file

# Calculate total number of tasks
CORES=$((SLURM_NNODES * SLURM_TASKS_PER_NODE))

# Load the required modules
module load openfoam/v2406 

#Load the python venv. First load the original python
module load  python/3.10.16
source /data/lmueller/.sim_venv/bin/activate  #now source the venv          

# Change into the working directory where the job was started
cd $SLURM_SUBMIT_DIR

# Run the tasks
python PreProcessing.py $CORES > PreProcessing.log
python Simulation.py $CORES > Simulation.log
