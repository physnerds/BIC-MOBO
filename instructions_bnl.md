# Introduction
This is the forked repository. The main difference is that it comes with the epic detector configuration files.

The idea is that you clone this repository. Use an appropriate eic container image in the cvmfs for the simulation for the PanDA jobs.

Run the scheduler_epic optimization to schedule the PanDA jobs of simulation and analysis. 

# Using the cvmfs container image 
 The container by itself is in the run_singularity.sh file. Make sure it points to the correct container.
 
 # Binding of the paths in the run_singularity.sh and make sure that the path points to the epic executables.

# Make sure that you copy the thisepic.sh from the cvmfs to local area if running locally