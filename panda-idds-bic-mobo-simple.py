import logging
import json
import getpass, os
from itertools import product
import sys,argparse

import AID2ETestTools as att
import EICMOBOTestTools as emt
# Global parameters here (Only needed for multi-step jobs)
global_parameters = {}

"""
# Panda runner script for BIC-MOBO
def RunPandaTrial(*args, **kwargs):
    #RunPandaTrial
    #Wrapper to run a single trial
    #of BIC-MOBO using the Panda runner.
    #Args:
    #ofResEle: output file to write electron resolution

    from EICMOBOTestTools import TrialManager as emt
    trialMgr = emt.TrialManager(
        run = kwargs["run_config"],
        par = kwargs["par_config"],
        ana = kwargs["obj_config"]
    )

    # more on this later
"""

"""
def RunObjectives():

    # create tag for trial
    time = str(datetime.datetime.now())
    time = re.sub(r'[.\-:\ ]', '', time)
    tag = f"AxTrial{time}"

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path = main_path + "/configuration/run.config"
    par_path = main_path + "/configuration/parameters.config"
    obj_path = main_path + "/configuration/objectives.config"

    # parse run config to extract path to eic-shell
    cfg_run   = emt.ReadJsonFile(run_path)
    eic_shell = cfg_run["eic_shell"]

    # create trial manager
    trial = emt.TrialManager(run_path,
                             par_path,
                             obj_path)

    # create and run script
    script, ofiles = trial.MakeTrialScript(tag, kwargs)
    #Make sure that the script exists
    print("Printing the scripts and ofiles ", script,ofiles)
    if not os.path.exists(script):
        raise FileNotFoundError(f"Script not found: {script}")
    else:
        print(f"Script found: {script}")
        os.chmod(script, 0o755)  # Ensure the script is executable
    
    result = subprocess.run([eic_shell, "--", script], capture_output=True, text=True, check=False)
    if returncode := result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"Trial script failed with return code {returncode}")

    # write out values of parameters to
    # output file(s) for analysis later
    ofResEle = ofiles["ElectronEnergyResolution"].replace(".root", ".txt")
    with open(ofResEle, 'a') as out:
        for param, value in kwargs.items():
            out.write("\n")
            out.write(f"{value}")

    # extract electron resolution
    eResEle = None
    with open(ofResEle, 'r') as out:
        outData = out.readlines()
        eResEle = float(outData[0])

    # return dictionary of objectives
    return {
        "objective" : eResEle
    }
"""

def RunObjectives(x,y):
    return {
        "objective": x+y
    }
# The main function to be called by the Panda runner
if __name__ == "__main__":
    """Panda BIC-MOBO main

    Main function to be called by
    the Panda runner to execute BIC-MOBO.
    """
    #import the ax-related modules here
    from ax.service.ax_client import AxClient, ObjectiveProperties
    #from ax.modelbridge.registry import Generators
    #from ax.modelbridge.generation_strategy import GenerationStrategy, GenerationStep
    from scheduler.utils.common import setup_logging
    from scheduler.job.job import JobType
    from scheduler import AxScheduler, JobLibRunner, PanDAiDDSRunner

    # setup logging
    #Available levels: "debug", "info", "warning", "error", "critical"
    setup_logging(log_level="debug")
    logging.debug("Initializing the ax client")
    ax_client = AxClient()

    # Now create the experiment
    logging.info("Create the experiment")
    # parameters are the detector parameters to be optimized.
    # I will assume that the main path is given by the environemnt variable AIDE_WORKDIR
    main_path = os.getenv("AIDE_WORKDIR", os.getcwd())
    # Config file paths
    par_path = os.path.join(main_path, "configuration/parameters.config")
    obj_path = os.path.join(main_path, "configuration/objectives.config")
    run_path = os.path.join(main_path, "configuration/run.config")
    # Get the configuration parameters from the json file
    cfg_par = emt.ReadJsonFile(par_path)
    cfg_obj = emt.ReadJsonFile(obj_path)
    cfg_run = emt.ReadJsonFile(run_path)

    eic_shell = cfg_run["eic_shell"]
    #
    # convert configuration parameters to ax-compliant ones
    cfg_par = att.ConvertParamConfig(cfg_par)
    cfg_obj = att.ConvertObjectConfig(cfg_obj)
    # print the configuration parameters and objectives
    print("Configuration parameters: ", cfg_par)
    print("Configuration objectives: ", cfg_obj)
    print("*****************************************************************")
    """
    ax_client.create_experiment(
        name="BIC-MOBO-Panda-Experiment",
        parameters = cfg_par,
        objectives = cfg_obj,
        )
    """
    ax_client.create_experiment(
        name="BIC-MOBO-Panda-Experiment",
        parameters = [
            {
                "name": "x",
                "type": "range",
                "bounds": [0.0, 10.0],
                "value_type": "float",
            },
            {
                "name": "y",
                "type": "range",
                "bounds": [0.0, 10.0],
                "value_type": "float",
            }
        ],
        objectives = {
            "objective": ObjectiveProperties(minimize=True)
        },
    )
    # Now need to initialize the environment for the Panda runner
    # setup_mamba contains ax related environment that might be neded during a PanDA job. 
    logging.info("Initializing the environment for the Panda runner")
    init_env = [
        "source /cvmfs/unpacked.cern.ch/registry.hub.docker.com/fyingtsai/eic_xl:24.11.1/opt/conda/setup_mamba.sh",
        "export AIDE_HOME=$(pwd);",
        "export AIDE_WORKDIR=$(pwd);",
        "command -v singularity &> /dev/null || export SINGULARITY=/cvmfs/oasis.opensciencegrid.org/mis/singularity/current/bin/singularity;",
        'alias singularity="$SINGULARITY";',
        'export SINGULARITY_OPTIONS="--bind /cvmfs:/cvmfs,$(pwd):$(pwd)"; ',
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly; export SINGULARITY_BINDPATH=/cvmfs; ",
        "source $AIDE_HOME/thisepic.sh;",
        "env; "
    ]
    init_env = " ".join(init_env)

    #Now create panda_attr dictionary
    dset_name_prefix = "user."+getpass.getuser()
    panda_attrs = {
        "name": dset_name_prefix,
        "init_env": init_env,
        "cloud": "US",
        "queue": "BNL_PanDA_1", # Test runs locally
        "source_dir":None,
        "source_dir_parent_level":1,
        "exclude_source_files":[
            r"(^|/)\.[^/]+", # hidden files and directories
            r"(^|/)out(/|$)",# directories called out and run are excluded
            r"(^|/)run(/|$)",
            "doc*",
            ".*log","examples",
            ".*txt","calibrations","fieldmaps","gdml","__pycache__" # calibrations dir has sym links
        ],
        "max_walltime":3600,
        "core_count":1,
        "total_memory":4000,
        "enable_separate_log":True,
        "job_dir":None,
    }

    #Create panda runner
    print("Creating PanDA iDDS runner")
    runner = PanDAiDDSRunner(**panda_attrs)

    # Now we can run the trial
    # This is not a multi step function...
    logging.info("Creating scheduler for a simple panda job")
    scheduler = AxScheduler(ax_client, runner)
    #set the objective
    scheduler.set_objective_function(RunObjectives)
    logging.info("Starting the optimization")

    best_param = scheduler.run_optimization(max_trials=10)
    print("Best parameters found: ", best_param)

