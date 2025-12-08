# December 8 2025
```bash
Printing the scripts and ofiles  /gpfs02/eic/abashyal2/BIC-MOBO/run/AxTrial20251208101123517846/do_aid2e_AxTrial20251208101123517846.sh {'ElectronEnergyResolution': '/gpfs02/eic/abashyal2/BIC-MOBO/out/AxTrial20251208101123517846/aid2e_AxTrial20251208101123517846_ana_single_electron_ElectronEnergyResolution.root'}
bash: line 1: /gpfs02/eic/abashyal2/BIC-MOBO/run/AxTrial20251208101123517846/do_aid2e_AxTrial20251208101123517846.sh: No such file or directory
Caught exception during execution job trial_0_job_613b5ce3 function: could not convert string to float: '\n'
joblib.externals.loky.process_executor._RemoteTraceback: 
```
Note that the bash script exists after the failed run. But need to make sure if it exists before the code tries to execute.

## Fixed the issue (path binding issue)

# No 